"""Cliente fino da Telegram Bot API (transporte apenas)."""
import httpx

from ..core.config import get_settings


def _token() -> str:
    s = get_settings()
    if not s.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN nao configurado")
    return s.telegram_bot_token


def _base() -> str:
    return f"https://api.telegram.org/bot{_token()}"


def enviar_mensagem(chat_id, texto: str):
    httpx.post(f"{_base()}/sendMessage", json={"chat_id": chat_id, "text": texto}, timeout=20)


def baixar_arquivo(file_id: str) -> tuple[bytes, str]:
    info = httpx.get(f"{_base()}/getFile", params={"file_id": file_id}, timeout=20).json()
    path = info["result"]["file_path"]
    url = f"https://api.telegram.org/file/bot{_token()}/{path}"
    conteudo = httpx.get(url, timeout=60).content
    return conteudo, path


def definir_webhook(url: str, secret: str):
    """Usado no Passo 7 (setWebhook)."""
    return httpx.post(
        f"{_base()}/setWebhook",
        json={"url": url, "secret_token": secret, "allowed_updates": ["message"]},
        timeout=20,
    ).json()
