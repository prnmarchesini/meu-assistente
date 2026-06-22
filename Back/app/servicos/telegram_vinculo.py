"""Vinculo de conta ao Telegram por codigo (uso unico, com expiracao)."""
import secrets
from datetime import datetime, timedelta, timezone

from .comuns import RegraNegocioError


def gerar_codigo(cur, user_id, minutos=10):
    codigo = f"{secrets.randbelow(10 ** 6):06d}"
    expira = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    cur.execute(
        "insert into telegram_codigos (user_id, codigo, expira_em) values (%s,%s,%s) returning *",
        (user_id, codigo, expira),
    )
    return cur.fetchone()


def consumir_codigo(cur, codigo, chat_id):
    """Valida o codigo e vincula o chat_id ao usuario. chat_id e unico."""
    cur.execute(
        "select * from telegram_codigos where codigo=%s and usado=false and expira_em > now()",
        (str(codigo).strip(),),
    )
    row = cur.fetchone()
    if not row:
        raise RegraNegocioError("codigo invalido ou expirado")
    # Garante unicidade do chat (um chat = uma conta): limpa vinculo anterior do chat.
    cur.execute(
        "update profiles set telegram_chat_id=null, telegram_habilitado=false where telegram_chat_id=%s",
        (chat_id,),
    )
    cur.execute(
        "update profiles set telegram_chat_id=%s, telegram_habilitado=true where id=%s",
        (chat_id, row["user_id"]),
    )
    cur.execute("update telegram_codigos set usado=true where id=%s", (row["id"],))
    return row["user_id"]


def usuario_por_chat(cur, chat_id):
    cur.execute(
        "select id from profiles where telegram_chat_id=%s and telegram_habilitado=true",
        (chat_id,),
    )
    r = cur.fetchone()
    return r["id"] if r else None


def desvincular(cur, user_id):
    cur.execute(
        "update profiles set telegram_chat_id=null, telegram_habilitado=false where id=%s",
        (user_id,),
    )
    return True


def status(cur, user_id):
    cur.execute(
        "select telegram_habilitado from profiles where id=%s", (user_id,)
    )
    r = cur.fetchone()
    return {"vinculado": bool(r and r["telegram_habilitado"])}
