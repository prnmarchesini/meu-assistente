"""Agregacoes do dashboard (decisao 19)."""
from datetime import date, timedelta

from .comuns import add_months, primeiro_dia


def resumo(cur, user_id):
    hoje = date.today()
    ini_mes = primeiro_dia(hoje)
    prox_mes = add_months(ini_mes, 1)

    # Total gasto no mes corrente (por data da despesa).
    cur.execute(
        "select coalesce(sum(valor_total),0) as total from despesas "
        "where user_id=%s and data>=%s and data<%s",
        (user_id, ini_mes, prox_mes),
    )
    total_mes = cur.fetchone()["total"]

    # Proxima fatura a vencer: fatura aberta com a menor data de vencimento futura.
    cur.execute(
        """select f.id, f.cartao_id, c.nome as cartao_nome, f.competencia,
                  min(p.vencimento) as vencimento,
                  coalesce(sum(p.valor),0) as total
           from faturas f
           join cartoes c on c.id = f.cartao_id
           left join parcelas p on p.fatura_id = f.id
           where f.user_id=%s and f.status='aberta'
           group by f.id, c.nome
           having min(p.vencimento) >= %s
           order by min(p.vencimento)
           limit 1""",
        (user_id, hoje),
    )
    proxima_fatura = cur.fetchone()

    # Garantias vencendo nos proximos 30 dias.
    cur.execute(
        """select id, fornecedor, tipo_documento, fim_garantia
           from documentos
           where user_id=%s and fim_garantia is not null
             and fim_garantia between %s and %s
           order by fim_garantia""",
        (user_id, hoje, hoje + timedelta(days=30)),
    )
    garantias = cur.fetchall()

    # Ultimas despesas.
    cur.execute(
        """select d.*, cat.nome as categoria_nome
           from despesas d
           left join categorias cat on cat.id = d.categoria_id
           where d.user_id=%s
           order by d.data desc, d.criado_em desc
           limit 10""",
        (user_id,),
    )
    ultimas = cur.fetchall()

    return {
        "total_mes": total_mes,
        "proxima_fatura": proxima_fatura,
        "garantias_a_vencer": garantias,
        "ultimas_despesas": ultimas,
    }
