"""Fixtures de teste.

Os testes de integracao rodam dentro de uma conexao cuja transacao e revertida
(rollback) no teardown — nada persiste no banco. Um usuario descartavel e criado
em auth.users (apenas o id; demais colunas tem default).
"""
import uuid

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from app.core.config import get_settings
from app.core.db import _parse


@pytest.fixture()
def conn():
    s = get_settings()
    assert s.database_url, "DATABASE_URL/DIRECT_URL nao configurado no .env"
    c = psycopg2.connect(connect_timeout=20, sslmode="require", **_parse(s.database_url))
    try:
        yield c
    finally:
        c.rollback()  # nada persiste
        c.close()


@pytest.fixture()
def cur(conn):
    c = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield c
    finally:
        c.close()


@pytest.fixture()
def user_id(cur):
    uid = str(uuid.uuid4())
    cur.execute("insert into auth.users (id) values (%s)", (uid,))
    return uid
