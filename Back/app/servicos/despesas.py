"""Despesas — criacao, edicao e exclusao (decisoes 1-3, 7, 8)."""
from datetime import date
from decimal import Decimal

from .comuns import RegraNegocioError
from .parcelas import alocar_parcelas

_CAMPOS_OPCIONAIS = ("categoria_id", "subcategoria_id", "local_id")


def _valida_pagamento(forma_pagamento, conta_id, cartao_id):
    if forma_pagamento not in ("conta", "cartao"):
        raise RegraNegocioError("forma_pagamento deve ser 'conta' ou 'cartao'")
    if forma_pagamento == "conta":
        if not conta_id or cartao_id:
            raise RegraNegocioError("pagamento por conta exige conta_id e nenhum cartao_id")
    else:
        if not cartao_id or conta_id:
            raise RegraNegocioError("pagamento por cartao exige cartao_id e nenhuma conta_id")


def _tem_parcela_em_fatura_paga(cur, user_id, despesa_id) -> bool:
    cur.execute(
        """select count(*) as n
           from parcelas p join faturas f on f.id = p.fatura_id
           where p.despesa_id=%s and p.user_id=%s and f.status='paga'""",
        (despesa_id, user_id),
    )
    return cur.fetchone()["n"] > 0


def criar_despesa(
    cur,
    user_id,
    *,
    descricao,
    valor_total,
    data: date,
    forma_pagamento,
    conta_id=None,
    cartao_id=None,
    num_parcelas=1,
    categoria_id=None,
    subcategoria_id=None,
    local_id=None,
):
    if not descricao or not str(descricao).strip():
        raise RegraNegocioError("descricao e obrigatoria")
    valor = Decimal(str(valor_total))
    if valor <= 0:
        raise RegraNegocioError("valor deve ser positivo")
    _valida_pagamento(forma_pagamento, conta_id, cartao_id)

    if forma_pagamento == "conta":
        num_parcelas = 1
    else:
        num_parcelas = int(num_parcelas or 1)
        if num_parcelas < 1:
            raise RegraNegocioError("numero de parcelas deve ser >= 1")

    cur.execute(
        """insert into despesas
           (user_id, descricao, valor_total, data, categoria_id, subcategoria_id,
            local_id, forma_pagamento, conta_id, cartao_id, num_parcelas)
           values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning *""",
        (
            user_id, str(descricao).strip(), valor, data, categoria_id, subcategoria_id,
            local_id, forma_pagamento, conta_id, cartao_id, num_parcelas,
        ),
    )
    despesa = cur.fetchone()

    parcelas = []
    if forma_pagamento == "cartao":
        parcelas = alocar_parcelas(
            cur, user_id, cartao_id, despesa["id"], data, num_parcelas, valor
        )
    return {"despesa": despesa, "parcelas": parcelas}


def editar_despesa(cur, user_id, despesa_id, **campos):
    """Atualiza a despesa. Mudar valor/parcelas re-aloca (apaga e recria).
    Bloqueia se houver parcela em fatura paga (decisao 7)."""
    cur.execute(
        "select * from despesas where id=%s and user_id=%s", (despesa_id, user_id)
    )
    atual = cur.fetchone()
    if not atual:
        raise RegraNegocioError("despesa nao encontrada")
    if _tem_parcela_em_fatura_paga(cur, user_id, despesa_id):
        raise RegraNegocioError(
            "despesa tem parcela em fatura paga; edicao bloqueada para preservar historico"
        )

    novo = dict(atual)
    novo.update({k: v for k, v in campos.items() if v is not None})

    forma = novo["forma_pagamento"]
    conta_id = novo.get("conta_id") if forma == "conta" else None
    cartao_id = novo.get("cartao_id") if forma == "cartao" else None
    _valida_pagamento(forma, conta_id, cartao_id)
    valor = Decimal(str(novo["valor_total"]))
    if valor <= 0:
        raise RegraNegocioError("valor deve ser positivo")
    num_parcelas = int(novo.get("num_parcelas") or 1) if forma == "cartao" else 1

    cur.execute(
        """update despesas set descricao=%s, valor_total=%s, data=%s,
           categoria_id=%s, subcategoria_id=%s, local_id=%s,
           forma_pagamento=%s, conta_id=%s, cartao_id=%s, num_parcelas=%s
           where id=%s and user_id=%s returning *""",
        (
            str(novo["descricao"]).strip(), valor, novo["data"],
            novo.get("categoria_id"), novo.get("subcategoria_id"), novo.get("local_id"),
            forma, conta_id, cartao_id, num_parcelas, despesa_id, user_id,
        ),
    )
    despesa = cur.fetchone()

    # Re-aloca parcelas (apaga e recria).
    cur.execute("delete from parcelas where despesa_id=%s and user_id=%s", (despesa_id, user_id))
    parcelas = []
    if forma == "cartao":
        parcelas = alocar_parcelas(
            cur, user_id, cartao_id, despesa_id, novo["data"], num_parcelas, valor
        )
    return {"despesa": despesa, "parcelas": parcelas}


def excluir_despesa(cur, user_id, despesa_id, confirmar=False):
    """Exclui com cascade nas parcelas. Se houver parcela em fatura paga,
    exige confirmar=True (decisao 8)."""
    cur.execute(
        "select id from despesas where id=%s and user_id=%s", (despesa_id, user_id)
    )
    if not cur.fetchone():
        raise RegraNegocioError("despesa nao encontrada")
    if _tem_parcela_em_fatura_paga(cur, user_id, despesa_id) and not confirmar:
        raise RegraNegocioError(
            "despesa tem parcela em fatura paga; confirme a exclusao (confirmar=True)"
        )
    cur.execute("delete from despesas where id=%s and user_id=%s", (despesa_id, user_id))
    return True


def listar_despesas(cur, user_id, inicio: date = None, fim: date = None, categoria_id=None, limite=100):
    cond = ["user_id=%s"]
    params = [user_id]
    if inicio:
        cond.append("data>=%s")
        params.append(inicio)
    if fim:
        cond.append("data<=%s")
        params.append(fim)
    if categoria_id:
        cond.append("categoria_id=%s")
        params.append(categoria_id)
    params.append(limite)
    cur.execute(
        f"select * from despesas where {' and '.join(cond)} order by data desc, criado_em desc limit %s",
        params,
    )
    return cur.fetchall()
