"""Testes PUROS da logica de parcelamento (sem banco)."""
from datetime import date
from decimal import Decimal

import pytest

from app.servicos.comuns import RegraNegocioError
from app.servicos.parcelas import (
    calcular_competencias,
    competencia_da_compra,
    dividir_valor,
    vencimento_da_fatura,
)


def test_divisao_100_em_3():
    assert dividir_valor("100.00", 3) == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]


def test_divisao_a_vista():
    assert dividir_valor("50.00", 1) == [Decimal("50.00")]


def test_divisao_exata():
    assert dividir_valor("90.00", 3) == [Decimal("30.00"), Decimal("30.00"), Decimal("30.00")]


@pytest.mark.parametrize("total", ["10.00", "99.99", "123.45", "0.03", "1000.01", "7.77"])
@pytest.mark.parametrize("n", list(range(1, 13)))
def test_soma_sempre_igual_ao_total(total, n):
    partes = dividir_valor(total, n)
    assert len(partes) == n
    assert sum(partes) == Decimal(total)
    assert all(p >= 0 for p in partes)


def test_divisao_parcelas_invalidas():
    with pytest.raises(RegraNegocioError):
        dividir_valor("100.00", 0)


def test_compra_antes_do_fechamento_cai_no_mes_corrente():
    assert competencia_da_compra(date(2025, 3, 5), 10) == date(2025, 3, 1)


def test_compra_depois_do_fechamento_cai_no_mes_seguinte():
    assert competencia_da_compra(date(2025, 3, 15), 10) == date(2025, 4, 1)


def test_compra_no_dia_do_fechamento_cai_no_mes_corrente():
    assert competencia_da_compra(date(2025, 3, 10), 10) == date(2025, 3, 1)


def test_virada_de_ano():
    # compra em dezembro apos o fechamento -> fatura de janeiro do ano seguinte
    assert competencia_da_compra(date(2025, 12, 20), 10) == date(2026, 1, 1)


def test_competencias_consecutivas_atravessam_o_ano():
    comps = calcular_competencias(date(2025, 12, 20), 10, 3)
    assert comps == [date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)]


def test_competencias_a_vista():
    assert calcular_competencias(date(2025, 6, 3), 10, 1) == [date(2025, 6, 1)]


def test_vencimento_clampa_fevereiro():
    assert vencimento_da_fatura(date(2025, 2, 1), 31) == date(2025, 2, 28)


def test_vencimento_normal():
    assert vencimento_da_fatura(date(2025, 3, 1), 15) == date(2025, 3, 15)
