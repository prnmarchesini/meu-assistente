"""Orquestrador: conversa em linguagem natural que aciona as tools.

O LLM (DeepSeek) escolhe ferramentas; o Python executa os servicos testados e
devolve o resultado ao modelo, em loop, ate a resposta final. Para acoes de
ESCRITA, o modelo resume e pede confirmacao antes de executar (decisao 12).
"""
import json

from openai import OpenAI

from ..core.config import get_settings
from .tools import DISPATCH, TOOLS_SPEC

MODELO = "deepseek-chat"
MAX_ITERACOES = 8

SYSTEM = (
    "Voce e um assistente financeiro em portugues do Brasil. Ajuda a registrar e "
    "consultar gastos, cartoes, faturas, garantias e documentos. "
    "Use SEMPRE as ferramentas para criar ou consultar dados — nunca invente numeros "
    "nem faca calculos de parcela/fatura por conta propria; isso vem das ferramentas. "
    "Antes de QUALQUER acao que grave dados (criar/alterar/marcar), resuma em uma frase "
    "o que entendeu e pergunte 'Confirmar?'. So chame a ferramenta de escrita depois que "
    "o usuario confirmar (ex.: 'sim'). Para consultas (leitura), responda direto. "
    "Datas no formato YYYY-MM-DD. Moeda BRL. Seja conciso."
)


def _client() -> OpenAI:
    s = get_settings()
    if not s.deepseek_api_key:
        raise RuntimeError("DEEPSEEK_API_KEY nao configurado")
    return OpenAI(api_key=s.deepseek_api_key, base_url="https://api.deepseek.com", timeout=60, max_retries=2)


def _serial(obj):
    return json.dumps(obj, ensure_ascii=False, default=str)


def conversar(cur, user_id, mensagem: str, historico=None):
    """Processa uma mensagem. `historico` e a lista de {role, content} anterior
    (texto apenas). Retorna {resposta, historico}."""
    historico = historico or []
    mensagens = [{"role": "system", "content": SYSTEM}] + historico + [
        {"role": "user", "content": mensagem}
    ]
    client = _client()

    for _ in range(MAX_ITERACOES):
        resp = client.chat.completions.create(
            model=MODELO, messages=mensagens, tools=TOOLS_SPEC, tool_choice="auto"
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            final = msg.content or ""
            novo = historico + [
                {"role": "user", "content": mensagem},
                {"role": "assistant", "content": final},
            ]
            return {"resposta": final, "historico": novo}

        # Registra a intencao do assistente (com tool_calls) e executa cada tool.
        mensagens.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            }
        )
        for tc in msg.tool_calls:
            nome = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
                fn = DISPATCH.get(nome)
                if not fn:
                    raise ValueError(f"ferramenta desconhecida: {nome}")
                resultado = fn(cur, user_id, **args)
                conteudo = _serial({"ok": True, "resultado": resultado})
            except Exception as e:  # noqa: BLE001
                conteudo = _serial({"ok": False, "erro": str(e)})
            mensagens.append({"role": "tool", "tool_call_id": tc.id, "content": conteudo})

    return {
        "resposta": "Nao consegui concluir a solicitacao. Pode reformular?",
        "historico": historico,
    }
