"""Logica de parcelamento e alocacao em faturas.

A parte de calculo (datas e divisao de valor) e composta por funcoes PURAS,
testaveis sem banco. A persistencia (`alocar_parcelas`) recebe o cursor como
dependencia e SEMPRE filtra por user_id.
"""
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from .comuns import RegraNegocioError, add_months, primeiro_dia, ultimo_dia_mes
from .faturas import obter_ou_criar_fatura

CENTAVO = Decimal("0.01")


def dividir_valor(valor_total, n_parcelas: int) -> list[Decimal]:
    """Divide o valor em n parcelas cuja soma e exatamente o total.

    O(s) primeiro(s) centavo(s) de resto vao para as primeiras parcelas
    (100,00 em 3x => 33,34 + 33,33 + 33,33).
    """
    if n_parcelas < 1:
        raise RegraNegocioError("numero de parcelas deve ser >= 1")
    total = Decimal(str(valor_total)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    if total <= 0:
        raise RegraNegocioError("valor deve ser positivo")
    cents = int((total * 100).to_integral_value())
    base, resto = divmod(cents, n_parcelas)
    valores = []
    for i in range(n_parcelas):
        c = base + (1 if i < resto else 0)
        valores.append((Decimal(c) / 100).quantize(CENTAVO))
    return valores


def competencia_da_compra(data_compra: date, dia_fechamento: int) -> date:
    """Competencia (dia 01) da fatura onde a 1a parcela cai.

    Compra ate o dia de fechamento -> fatura do mes corrente;
    depois do fechamento -> fatura seguinte.
    """
    base = primeiro_dia(data_compra)
    if data_compra.day <= dia_fechamento:
        return base
    return add_months(base, 1)


def calcular_competencias(data_compra: date, dia_fechamento: int, n_parcelas: int) -> list[date]:
    """Competencias consecutivas (uma por parcela), tratando virada de ano."""
    if n_parcelas < 1:
        raise RegraNegocioError("numero de parcelas deve ser >= 1")
    primeira = competencia_da_compra(data_compra, dia_fechamento)
    return [add_months(primeira, i) for i in range(n_parcelas)]


def vencimento_da_fatura(competencia: date, dia_vencimento: int) -> date:
    dia = min(dia_vencimento, ultimo_dia_mes(competencia.year, competencia.month))
    return date(competencia.year, competencia.month, dia)


def alocar_parcelas(cur, user_id, cartao_id, despesa_id, data_compra, n_parcelas, valor_total):
    """Cria as parcelas distribuidas nas faturas consecutivas. Garante
    sum(parcelas.valor) == valor_total."""
    cur.execute(
        "select dia_fechamento, dia_vencimento from cartoes where id=%s and user_id=%s",
        (cartao_id, user_id),
    )
    cartao = cur.fetchone()
    if not cartao:
        raise RegraNegocioError("cartao nao encontrado")

    comps = calcular_competencias(data_compra, cartao["dia_fechamento"], n_parcelas)
    valores = dividir_valor(valor_total, n_parcelas)

    parcelas = []
    for i, (comp, valor) in enumerate(zip(comps, valores), start=1):
        fatura = obter_ou_criar_fatura(cur, user_id, cartao_id, comp)
        venc = vencimento_da_fatura(comp, cartao["dia_vencimento"])
        cur.execute(
            """insert into parcelas (user_id, despesa_id, fatura_id, numero, valor, vencimento)
               values (%s,%s,%s,%s,%s,%s) returning *""",
            (user_id, despesa_id, fatura["id"], i, valor, venc),
        )
        parcelas.append(cur.fetchone())
    return parcelas
