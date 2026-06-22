"""Utilitarios compartilhados pelos servicos."""
import calendar
from datetime import date


class RegraNegocioError(Exception):
    """Erro de regra de negocio / entrada invalida (vira HTTP 400 na API)."""


def normalizar_nome(nome: str) -> str:
    """Trim + colapsa espacos internos. A comparacao case-insensitive de
    duplicatas e feita no banco (indice unico sobre lower(nome)) — decisao 18."""
    if nome is None:
        raise RegraNegocioError("nome e obrigatorio")
    limpo = " ".join(str(nome).strip().split())
    if not limpo:
        raise RegraNegocioError("nome nao pode ser vazio")
    return limpo


def ultimo_dia_mes(ano: int, mes: int) -> int:
    return calendar.monthrange(ano, mes)[1]


def primeiro_dia(d: date) -> date:
    return date(d.year, d.month, 1)


def add_months(d: date, n: int) -> date:
    """Soma n meses preservando o dia quando possivel (clampa ao ultimo dia)."""
    total = (d.year * 12 + (d.month - 1)) + n
    ano, mes0 = divmod(total, 12)
    mes = mes0 + 1
    dia = min(d.day, ultimo_dia_mes(ano, mes))
    return date(ano, mes, dia)
