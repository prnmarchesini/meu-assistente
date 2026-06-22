"""Conexao com o Postgres do Supabase.

A senha pode conter caracteres especiais (ex.: '#') que quebram o parser de URL
padrao, entao fazemos o parse manualmente.
"""
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import get_settings


def _parse(url: str) -> dict:
    body = url.split("://", 1)[1]
    creds, hostpart = body.rsplit("@", 1)
    user, pwd = creds.split(":", 1)
    hostport, db = hostpart.split("/", 1)
    host, port = hostport.rsplit(":", 1)
    return dict(host=host, port=int(port), user=user, password=pwd, dbname=db.split("?")[0])


@contextmanager
def get_connection():
    """Conexao de curta duracao. Use em `with get_connection() as conn:`."""
    s = get_settings()
    if not s.database_url:
        raise RuntimeError("Nenhuma URL de banco configurada (SUPABASE_POOLER_URL / DIRECT_URL).")
    conn = psycopg2.connect(connect_timeout=15, sslmode="require", **_parse(s.database_url))
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(commit: bool = False):
    """Cursor com dict-rows. `commit=True` confirma ao final."""
    with get_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()


def check_connection() -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select 1")
            return cur.fetchone()[0] == 1
