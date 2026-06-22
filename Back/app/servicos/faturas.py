"""Faturas — criadas sob demanda; competencia sempre no dia 01."""
from datetime import date

from .comuns import RegraNegocioError, primeiro_dia


def obter_ou_criar_fatura(cur, user_id, cartao_id, competencia: date):
    """Retorna a fatura (cartao, competencia), criando se nao existir.
    Respeita o unique(cartao_id, competencia)."""
    comp = primeiro_dia(competencia)
    cur.execute(
        """insert into faturas (user_id, cartao_id, competencia)
           values (%s,%s,%s)
           on conflict (cartao_id, competencia) do nothing
           returning *""",
        (user_id, cartao_id, comp),
    )
    row = cur.fetchone()
    if row:
        return row
    cur.execute(
        "select * from faturas where cartao_id=%s and competencia=%s",
        (cartao_id, comp),
    )
    return cur.fetchone()


def consultar_fatura(cur, user_id, cartao_id, competencia: date):
    comp = primeiro_dia(competencia)
    cur.execute(
        "select * from faturas where user_id=%s and cartao_id=%s and competencia=%s",
        (user_id, cartao_id, comp),
    )
    fatura = cur.fetchone()
    if not fatura:
        return None
    cur.execute(
        """select p.*, d.descricao
           from parcelas p join despesas d on d.id = p.despesa_id
           where p.fatura_id=%s order by p.vencimento""",
        (fatura["id"],),
    )
    fatura = dict(fatura)
    fatura["parcelas"] = cur.fetchall()
    fatura["total"] = sum((p["valor"] for p in fatura["parcelas"]), start=0)
    return fatura


def marcar_fatura_paga(cur, user_id, cartao_id, competencia: date):
    """Marca como paga (so muda status, preserva historico) — decisao 9."""
    comp = primeiro_dia(competencia)
    cur.execute(
        """update faturas set status='paga', pago_em=now()
           where user_id=%s and cartao_id=%s and competencia=%s returning *""",
        (user_id, cartao_id, comp),
    )
    row = cur.fetchone()
    if not row:
        raise RegraNegocioError("fatura nao encontrada")
    return row


def proximas_faturas(cur, user_id, cartao_id=None):
    hoje = date.today()
    if cartao_id:
        cur.execute(
            """select f.*, c.nome as cartao_nome from faturas f
               join cartoes c on c.id=f.cartao_id
               where f.user_id=%s and f.cartao_id=%s and f.competencia>=%s
               order by f.competencia""",
            (user_id, cartao_id, primeiro_dia(hoje)),
        )
    else:
        cur.execute(
            """select f.*, c.nome as cartao_nome from faturas f
               join cartoes c on c.id=f.cartao_id
               where f.user_id=%s and f.competencia>=%s
               order by f.competencia""",
            (user_id, primeiro_dia(hoje)),
        )
    return cur.fetchall()
