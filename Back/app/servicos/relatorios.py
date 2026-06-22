"""Relatorios de leitura (usados pelas tools de IA e pela API)."""
from datetime import date, timedelta

from .comuns import add_months, primeiro_dia


def periodo_mes_atual():
    ini = primeiro_dia(date.today())
    return ini, add_months(ini, 1) - timedelta(days=1)


def total_por_periodo(cur, user_id, inicio: date, fim: date):
    cur.execute(
        """select coalesce(sum(valor_total),0) as total, count(*) as quantidade
           from despesas where user_id=%s and data>=%s and data<=%s""",
        (user_id, inicio, fim),
    )
    return cur.fetchone()


def total_por_categoria(cur, user_id, inicio: date, fim: date):
    cur.execute(
        """select coalesce(c.nome,'Sem categoria') as categoria,
                  coalesce(sum(d.valor_total),0) as total
           from despesas d
           left join categorias c on c.id = d.categoria_id
           where d.user_id=%s and d.data>=%s and d.data<=%s
           group by c.nome
           order by total desc""",
        (user_id, inicio, fim),
    )
    return cur.fetchall()
