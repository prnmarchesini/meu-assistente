"""Testes da camada de API (Passo 3).

Sobrescrevemos a autenticacao (injeta um user_id de teste) e o cursor (uma
transacao compartilhada, revertida no fim) — assim exercitamos rotas + servicos
+ serializacao de ponta a ponta, sem precisar de um token real do Supabase.
"""
import uuid

import psycopg2
import pytest
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from app.api import auth as auth_mod
from app.api import deps as deps_mod
from app.core.config import get_settings
from app.core.db import _parse
from app.main import app


@pytest.fixture()
def api():
    s = get_settings()
    conn = psycopg2.connect(connect_timeout=20, sslmode="require", **_parse(s.database_url))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    uid = str(uuid.uuid4())
    cur.execute("insert into auth.users (id) values (%s)", (uid,))

    app.dependency_overrides[auth_mod.get_current_user_id] = lambda: uid

    def _db():
        yield cur  # mesma transacao em todas as requisicoes do teste

    app.dependency_overrides[deps_mod.get_db] = _db
    try:
        with TestClient(app) as client:
            yield client, uid
    finally:
        app.dependency_overrides.clear()
        conn.rollback()
        cur.close()
        conn.close()


def test_categoria_crud_e_normalizacao(api):
    client, _ = api
    r = client.post("/categorias", json={"nome": "Mercado"})
    assert r.status_code == 201
    r2 = client.post("/categorias", json={"nome": "mercado"})
    assert r2.json()["id"] == r.json()["id"]
    listagem = client.get("/categorias").json()
    assert len(listagem) == 1


def test_fluxo_despesa_cartao(api):
    client, _ = api
    cartao = client.post(
        "/cartoes",
        json={"nome": "Nubank", "dia_fechamento": 10, "dia_vencimento": 17},
    ).json()
    r = client.post(
        "/despesas",
        json={
            "descricao": "Mercado", "valor_total": "200.00", "data": "2025-03-05",
            "forma_pagamento": "cartao", "cartao_id": cartao["id"], "num_parcelas": 2,
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert len(body["parcelas"]) == 2
    fatura = client.get(f"/faturas/{cartao['id']}/2025-03-01").json()
    assert len(fatura["parcelas"]) == 1


def test_erro_regra_negocio_vira_400(api):
    client, _ = api
    r = client.post(
        "/despesas",
        json={
            "descricao": "x", "valor_total": "10.00", "data": "2025-03-05",
            "forma_pagamento": "cartao",  # sem cartao_id
        },
    )
    assert r.status_code == 400


def test_dashboard(api):
    client, _ = api
    conta = client.post("/contas", json={"nome": "Carteira"}).json()
    client.post(
        "/despesas",
        json={
            "descricao": "Cafe", "valor_total": "12.00", "data": "2025-06-01",
            "forma_pagamento": "conta", "conta_id": conta["id"],
        },
    )
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "total_mes" in r.json()
    assert "ultimas_despesas" in r.json()


def test_seed_categorias(api):
    client, _ = api
    r = client.post("/seed-categorias", json={})
    assert r.status_code == 200
    assert len(r.json()) == 6


def test_rota_exige_autenticacao():
    """Sem override de auth, uma rota protegida deve recusar requisicao sem token."""
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        r = client.get("/categorias")  # sem Authorization
        assert r.status_code in (401, 403)
