"""Roteamento das mensagens do Telegram.

Adaptador fino: identifica o usuario, transcreve audio, processa foto e delega
texto ao orquestrador (Passo 5). Nenhuma regra de negocio aqui.
"""
import json

from ..ia import orquestrador, pipeline_doc
from ..ia.openai_client import transcrever_audio
from ..servicos import telegram_vinculo as tv
from ..servicos.comuns import RegraNegocioError
from . import bot

_INSTRUCAO_VINCULO = (
    "Seu chat ainda nao esta vinculado. Entre no site, va ao seu perfil, gere um "
    "codigo e me envie: /start CODIGO"
)
_MAX_HIST = 10


def _hist_load(cur, chat_id):
    cur.execute("select historico from telegram_conversas where chat_id=%s", (chat_id,))
    r = cur.fetchone()
    return r["historico"] if r and r["historico"] else []


def _hist_save(cur, chat_id, historico):
    cur.execute(
        """insert into telegram_conversas (chat_id, historico, atualizado_em)
           values (%s, %s::jsonb, now())
           on conflict (chat_id) do update
             set historico = excluded.historico, atualizado_em = now()""",
        (chat_id, json.dumps(historico[-_MAX_HIST:])),
    )


def _responder(cur, chat_id, user_id, mensagem):
    historico = _hist_load(cur, chat_id)
    r = orquestrador.conversar(cur, user_id, mensagem, historico)
    _hist_save(cur, chat_id, r["historico"])
    bot.enviar_mensagem(chat_id, r["resposta"])


def handle_update(cur, update: dict):
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    texto = (msg.get("text") or "").strip()

    # Vinculo: /start CODIGO
    if texto.startswith("/start"):
        partes = texto.split(maxsplit=1)
        if len(partes) == 2 and partes[1].strip():
            try:
                tv.consumir_codigo(cur, partes[1].strip(), chat_id)
                bot.enviar_mensagem(chat_id, "Conta vinculada com sucesso! Agora e so falar comigo.")
            except RegraNegocioError as e:
                bot.enviar_mensagem(chat_id, f"Nao consegui vincular: {e}")
        else:
            bot.enviar_mensagem(chat_id, "Ola! " + _INSTRUCAO_VINCULO)
        return

    user_id = tv.usuario_por_chat(cur, chat_id)
    if not user_id:
        bot.enviar_mensagem(chat_id, _INSTRUCAO_VINCULO)
        return

    # Audio -> Whisper -> mostra transcricao -> orquestrador (decisoes 13, 14)
    media = msg.get("voice") or msg.get("audio")
    if media:
        conteudo, path = bot.baixar_arquivo(media["file_id"])
        transcricao = transcrever_audio(conteudo, nome=path.split("/")[-1])
        bot.enviar_mensagem(chat_id, f'Entendi: "{transcricao}"')
        _responder(cur, chat_id, user_id, transcricao)
        return

    # Foto de nota -> pipeline do Passo 4
    if msg.get("photo"):
        file_id = msg["photo"][-1]["file_id"]  # maior resolucao
        conteudo, path = bot.baixar_arquivo(file_id)
        res = pipeline_doc.processar_documento(cur, user_id, conteudo, path.split("/")[-1], "image/jpeg")
        d = res["sugestao_despesa"]
        valor = d.get("valor_total")
        bot.enviar_mensagem(
            chat_id,
            f"Documento recebido. Identifiquei: {d.get('descricao')}"
            + (f", R$ {valor}" if valor else "")
            + ". Quer que eu lance como despesa? Me diga a forma de pagamento.",
        )
        return

    # Texto livre -> motor
    if texto:
        _responder(cur, chat_id, user_id, texto)
