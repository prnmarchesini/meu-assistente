"""Endpoint de chat (Passo 5) — testa o motor pelo site antes do Telegram."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..ia.orquestrador import conversar
from .auth import get_current_user_id
from .deps import get_db

router = APIRouter(dependencies=[Depends(get_current_user_id)])


class ChatIn(BaseModel):
    mensagem: str
    historico: list[dict] = []


@router.post("/chat")
def chat(body: ChatIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return conversar(cur, uid, body.mensagem, body.historico)
