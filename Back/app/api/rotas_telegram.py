"""Rotas do Telegram: webhook (publico, validado por secret) + vinculo (auth)."""
from fastapi import APIRouter, Depends, Header, HTTPException, Request

from ..core.config import get_settings
from ..core.ratelimit import permitir
from ..servicos import telegram_vinculo as tv
from ..telegram.webhook import handle_update
from .auth import get_current_user_id
from .deps import get_db

router = APIRouter()


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
    cur=Depends(get_db),
):
    s = get_settings()
    # Hardening (Passo 7): rejeita qualquer chamada sem o secret correto.
    if not s.telegram_webhook_secret or x_telegram_bot_api_secret_token != s.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="secret invalido")
    # Rate limit por IP de origem (defesa contra flood).
    ip = request.client.host if request.client else "desconhecido"
    if not permitir(f"webhook:{ip}", limite=60, janela_s=60):
        raise HTTPException(status_code=429, detail="muitas requisicoes")
    update = await request.json()
    try:
        handle_update(cur, update)
    except Exception:  # noqa: BLE001 — webhook nunca deve devolver erro ao Telegram
        pass
    return {"ok": True}


@router.post("/telegram/gerar-codigo")
def gerar_codigo(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    s = get_settings()
    codigo = tv.gerar_codigo(cur, uid)
    resp = {"codigo": codigo["codigo"], "expira_em": codigo["expira_em"]}
    usuario_bot = getattr(s, "telegram_bot_username", None)
    if usuario_bot:
        resp["deep_link"] = f"https://t.me/{usuario_bot}?start={codigo['codigo']}"
    return resp


@router.post("/telegram/desvincular")
def desvincular(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    tv.desvincular(cur, uid)
    return {"ok": True}


@router.get("/telegram/status")
def status(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return tv.status(cur, uid)
