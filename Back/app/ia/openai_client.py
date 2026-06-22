"""Wrappers da OpenAI: embeddings, visao (OCR/estruturacao) e transcricao.

Modelos centralizados aqui para facilitar troca. Inclui timeout e retry simples
(decisao do Passo 7: tratamento de falha das APIs externas).
"""
import base64
import json
import time

from openai import OpenAI

from ..core.config import get_settings

MODELO_EMBEDDING = "text-embedding-3-small"
DIM_EMBEDDING = 1536
MODELO_VISAO = "gpt-4o"          # OCR + estruturacao de imagem
MODELO_ESTRUTURA = "gpt-4o"      # estruturacao a partir de texto
MODELO_TRANSCRICAO = "whisper-1"  # Passo 6


def _client() -> OpenAI:
    s = get_settings()
    if not s.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY nao configurado")
    return OpenAI(api_key=s.openai_api_key, timeout=60, max_retries=2)


def _com_retry(fn, tentativas=3, espera=2):
    ultimo = None
    for i in range(tentativas):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(espera * (i + 1))
    raise ultimo


def gerar_embedding(texto: str) -> list[float]:
    texto = (texto or "").strip() or " "
    resp = _com_retry(
        lambda: _client().embeddings.create(model=MODELO_EMBEDDING, input=texto[:8000])
    )
    return resp.data[0].embedding


_PROMPT_ESTRUTURA = (
    "Voce extrai dados de documentos financeiros (notas fiscais, recibos, garantias). "
    "Responda APENAS um JSON com as chaves: "
    "fornecedor (string ou null), valor_total (numero ou null), "
    "data_documento (YYYY-MM-DD ou null), fim_garantia (YYYY-MM-DD ou null), "
    "tipo_documento (um de: nota_fiscal, recibo, garantia, outro). "
    "Use null quando a informacao nao estiver presente."
)


def estruturar_texto(texto: str) -> dict:
    resp = _com_retry(
        lambda: _client().chat.completions.create(
            model=MODELO_ESTRUTURA,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _PROMPT_ESTRUTURA},
                {"role": "user", "content": f"Texto do documento:\n{texto[:12000]}"},
            ],
        )
    )
    return json.loads(resp.choices[0].message.content)


def estruturar_imagem(conteudo: bytes, mime: str) -> dict:
    b64 = base64.b64encode(conteudo).decode()
    data_url = f"data:{mime};base64,{b64}"
    resp = _com_retry(
        lambda: _client().chat.completions.create(
            model=MODELO_VISAO,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _PROMPT_ESTRUTURA},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extraia os campos deste documento."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
        )
    )
    return json.loads(resp.choices[0].message.content)


def transcrever_audio(conteudo: bytes, nome="audio.ogg") -> str:
    """Whisper transcreve/traduz para texto (decisao 14 — Passo 6)."""
    import io

    arquivo = io.BytesIO(conteudo)
    arquivo.name = nome
    resp = _com_retry(
        lambda: _client().audio.transcriptions.create(model=MODELO_TRANSCRICAO, file=arquivo)
    )
    return resp.text
