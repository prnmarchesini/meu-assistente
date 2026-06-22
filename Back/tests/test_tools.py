"""Testes da camada de tools (Passo 5), sem o LLM — deterministicos.

O loop do orquestrador com o DeepSeek e validado a parte (script live); aqui
garantimos que cada tool resolve nomes->ids e chama os servicos corretamente.
"""
from datetime import date
from decimal import Decimal

import pytest

from app.ia import tools
from app.servicos import cadastros
from app.servicos.comuns import RegraNegocioError


def test_tool_criar_despesa_resolve_nomes(cur, user_id):
    cadastros.criar_cartao(cur, user_id, "Nubank", dia_fechamento=10, dia_vencimento=17)
    r = tools.criar_despesa(
        cur, user_id, descricao="Mercado", valor=200, data="2025-03-05",
        forma_pagamento="cartao", cartao="Nubank", num_parcelas=2, categoria="Mercado",
    )
    assert len(r["parcelas"]) == 2
    assert sum(p["valor"] for p in r["parcelas"]) == Decimal("200.00")
    # categoria foi criada por nome
    assert any(c["nome"] == "Mercado" for c in cadastros.listar_categorias(cur, user_id))


def test_tool_criar_despesa_cartao_inexistente(cur, user_id):
    with pytest.raises(RegraNegocioError):
        tools.criar_despesa(
            cur, user_id, descricao="x", valor=10, data="2025-03-05",
            forma_pagamento="cartao", cartao="Inexistente",
        )


def test_tool_despesa_por_conta(cur, user_id):
    r = tools.criar_despesa(
        cur, user_id, descricao="Padaria", valor=15, data="2025-03-05",
        forma_pagamento="conta", conta="Carteira",
    )
    assert r["parcelas"] == []


def test_tool_total_por_periodo(cur, user_id):
    tools.criar_despesa(cur, user_id, descricao="A", valor=100, data="2025-03-10",
                        forma_pagamento="conta", conta="C")
    tools.criar_despesa(cur, user_id, descricao="B", valor=50, data="2025-03-20",
                        forma_pagamento="conta", conta="C")
    r = tools.total_por_periodo(cur, user_id, "2025-03-01", "2025-03-31")
    assert r["total"] == Decimal("150.00")
    assert r["quantidade"] == 2


def test_tool_total_por_categoria(cur, user_id):
    tools.criar_despesa(cur, user_id, descricao="A", valor=100, data="2025-03-10",
                        forma_pagamento="conta", conta="C", categoria="Mercado")
    r = tools.total_por_periodo(cur, user_id, "2025-03-01", "2025-03-31", agrupar_por="categoria")
    assert any(linha["categoria"] == "Mercado" and linha["total"] == Decimal("100.00") for linha in r)


def test_tool_marcar_fatura_paga(cur, user_id):
    cadastros.criar_cartao(cur, user_id, "Nu", dia_fechamento=10, dia_vencimento=17)
    tools.criar_despesa(cur, user_id, descricao="x", valor=100, data="2025-03-05",
                        forma_pagamento="cartao", cartao="Nu", num_parcelas=1)
    f = tools.marcar_fatura_paga(cur, user_id, "Nu", "2025-03-01")
    assert f["status"] == "paga"


def test_tool_listar_despesas(cur, user_id):
    tools.criar_despesa(cur, user_id, descricao="A", valor=10, data="2025-03-10",
                        forma_pagamento="conta", conta="C")
    assert len(tools.listar_despesas(cur, user_id)) == 1
