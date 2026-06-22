"""Endpoint de chat (Passo 5) — testa o motor pelo site antes do Telegram."""
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..ia.orquestrador import conversar
from .auth import get_current_user_id
from .deps import get_db

log = logging.getLogger("app.chat")
router = APIRouter(dependencies=[Depends(get_current_user_id)])


class ChatIn(BaseModel):
    mensagem: str
    historico: list[dict] = []


@router.post("/chat")
def chat(body: ChatIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    try:
        return conversar(cur, uid, body.mensagem, body.historico)
    except Exception:  # noqa: BLE001 — falha de API externa nao deve virar 500 cru
        log.exception("falha no chat")
        return {
            "resposta": "Estou com dificuldade para responder agora. Tente novamente em instantes.",
            "historico": body.historico,
        }
