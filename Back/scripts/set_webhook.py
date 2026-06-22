"""Configura o webhook do Telegram apontando para o backend em producao.

Uso:
    python scripts/set_webhook.py https://SEU-BACKEND.up.railway.app

Le TELEGRAM_BOT_TOKEN e TELEGRAM_WEBHOOK_SECRET do ambiente / .env.
"""
import sys

import httpx

sys.path.insert(0, ".")
from app.core.config import get_settings  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("uso: python scripts/set_webhook.py https://backend.up.railway.app")
        sys.exit(1)
    base_backend = sys.argv[1].rstrip("/")
    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_webhook_secret:
        print("Defina TELEGRAM_BOT_TOKEN e TELEGRAM_WEBHOOK_SECRET no .env / ambiente.")
        sys.exit(1)
    url = f"{base_backend}/telegram/webhook"
    r = httpx.post(
        f"https://api.telegram.org/bot{s.telegram_bot_token}/setWebhook",
        json={"url": url, "secret_token": s.telegram_webhook_secret, "allowed_updates": ["message"]},
        timeout=20,
    )
    print(r.status_code, r.text)


if __name__ == "__main__":
    main()
