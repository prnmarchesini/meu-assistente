"""Testes de integracao dos servicos (banco real, transacao revertida)."""
from datetime import date
from decimal import Decimal

import pytest

from app.servicos import cadastros, despesas, faturas
from app.servicos.comuns import RegraNegocioError


def test_normalizacao_nao_duplica_categoria(cur, user_id):
    a = cadastros.criar_categoria(cur, user_id, "Mercado")
    b = cadastros.criar_categoria(cur, user_id, "mercado")
    c = cadastros.criar_categoria(cur, user_id, "  MERCADO  ")
    assert a["id"] == b["id"] == c["id"]
    assert len(cadastros.listar_categorias(cur, user_id)) == 1


def test_despesa_por_conta_nao_gera_parcela(cur, user_id):
    conta = cadastros.criar_conta(cur, user_id, "Nubank Conta", "corrente")
    r = despesas.criar_despesa(
        cur, user_id, descricao="Padaria", valor_total="20.00",
        data=date(2025, 3, 1), forma_pagamento="conta", conta_id=conta["id"],
    )
    assert r["parcelas"] == []
    assert r["despesa"]["num_parcelas"] == 1


def test_despesa_cartao_parcelada_soma_exata_e_faturas_certas(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Nubank", dia_fechamento=10, dia_vencimento=17)
    r = despesas.criar_despesa(
        cur, user_id, descricao="Mercado", valor_total="200.00",
        data=date(2025, 3, 5), forma_pagamento="cartao", cartao_id=cartao["id"], num_parcelas=2,
    )
    parcelas = sorted(r["parcelas"], key=lambda p: p["numero"])
    assert len(parcelas) == 2
    assert sum(p["valor"] for p in parcelas) == Decimal("200.00")
    # compra dia 5 <= fechamento 10 => 1a parcela competencia marco/2025
    f1 = faturas.consultar_fatura(cur, user_id, cartao["id"], date(2025, 3, 1))
    f2 = faturas.consultar_fatura(cur, user_id, cartao["id"], date(2025, 4, 1))
    assert f1 is not None and f2 is not None
    assert len(f1["parcelas"]) == 1 and len(f2["parcelas"]) == 1


def test_despesa_a_vista_no_cartao_uma_parcela(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Inter", dia_fechamento=10, dia_vencimento=17)
    r = despesas.criar_despesa(
        cur, user_id, descricao="Livro", valor_total="59.90",
        data=date(2025, 3, 5), forma_pagamento="cartao", cartao_id=cartao["id"], num_parcelas=1,
    )
    assert len(r["parcelas"]) == 1
    assert r["parcelas"][0]["valor"] == Decimal("59.90")


def test_soma_parcelas_igual_valor_total_varios_casos(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Visa", dia_fechamento=10, dia_vencimento=17)
    for valor, n in [("100.00", 3), ("99.99", 7), ("1000.01", 12), ("10.00", 4)]:
        r = despesas.criar_despesa(
            cur, user_id, descricao="x", valor_total=valor, data=date(2025, 1, 5),
            forma_pagamento="cartao", cartao_id=cartao["id"], num_parcelas=n,
        )
        assert sum(p["valor"] for p in r["parcelas"]) == Decimal(valor)


def test_fatura_unica_por_competencia(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Master", dia_fechamento=10, dia_vencimento=17)
    f1 = faturas.obter_ou_criar_fatura(cur, user_id, cartao["id"], date(2025, 3, 1))
    f2 = faturas.obter_ou_criar_fatura(cur, user_id, cartao["id"], date(2025, 3, 20))  # normaliza p/ 01
    assert f1["id"] == f2["id"]


def test_coerencia_conta_cartao(cur, user_id):
    with pytest.raises(RegraNegocioError):
        despesas.criar_despesa(
            cur, user_id, descricao="x", valor_total="10.00", data=date(2025, 3, 1),
            forma_pagamento="cartao",  # sem cartao_id
        )
    with pytest.raises(RegraNegocioError):
        despesas.criar_despesa(
            cur, user_id, descricao="x", valor_total="10.00", data=date(2025, 3, 1),
            forma_pagamento="conta",  # sem conta_id
        )


def test_edicao_bloqueada_quando_parcela_em_fatura_paga(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Elo", dia_fechamento=10, dia_vencimento=17)
    r = despesas.criar_despesa(
        cur, user_id, descricao="TV", valor_total="200.00", data=date(2025, 3, 5),
        forma_pagamento="cartao", cartao_id=cartao["id"], num_parcelas=2,
    )
    faturas.marcar_fatura_paga(cur, user_id, cartao["id"], date(2025, 3, 1))
    with pytest.raises(RegraNegocioError):
        despesas.editar_despesa(cur, user_id, r["despesa"]["id"], valor_total="300.00")


def test_exclusao_exige_confirmacao_se_fatura_paga(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Hiper", dia_fechamento=10, dia_vencimento=17)
    r = despesas.criar_despesa(
        cur, user_id, descricao="Geladeira", valor_total="200.00", data=date(2025, 3, 5),
        forma_pagamento="cartao", cartao_id=cartao["id"], num_parcelas=2,
    )
    did = r["despesa"]["id"]
    faturas.marcar_fatura_paga(cur, user_id, cartao["id"], date(2025, 3, 1))
    with pytest.raises(RegraNegocioError):
        despesas.excluir_despesa(cur, user_id, did)  # sem confirmar
    assert despesas.excluir_despesa(cur, user_id, did, confirmar=True) is True


def test_edicao_realoca_parcelas(cur, user_id):
    cartao = cadastros.criar_cartao(cur, user_id, "Card", dia_fechamento=10, dia_vencimento=17)
    r = despesas.criar_despesa(
        cur, user_id, descricao="Curso", valor_total="100.00", data=date(2025, 3, 5),
        forma_pagamento="cartao", cartao_id=cartao["id"], num_parcelas=2,
    )
    r2 = despesas.editar_despesa(cur, user_id, r["despesa"]["id"], valor_total="300.00", num_parcelas=3)
    assert len(r2["parcelas"]) == 3
    assert sum(p["valor"] for p in r2["parcelas"]) == Decimal("300.00")
