"""Rotas REST sobre os servicos do Passo 2 (+ dashboard).

Toda rota injeta o user_id a partir do JWT verificado; o cliente nunca o envia.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..servicos import cadastros, dashboard, despesas, faturas
from .auth import get_current_user_id
from .deps import get_db
from .schemas import (
    CartaoIn,
    ContaIn,
    DespesaEditIn,
    DespesaIn,
    MarcarFaturaPagaIn,
    NomeIn,
    SeedIn,
    SubcategoriaIn,
)

router = APIRouter(dependencies=[Depends(get_current_user_id)])


# ───────────────── Categorias / Subcategorias ─────────────────
@router.get("/categorias")
def listar_categorias(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.listar_categorias(cur, uid)


@router.post("/categorias", status_code=201)
def criar_categoria(body: NomeIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.criar_categoria(cur, uid, body.nome)


@router.delete("/categorias/{id_}")
def excluir_categoria(id_: str, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    cadastros.excluir_categoria(cur, uid, id_)
    return {"ok": True}


@router.get("/subcategorias")
def listar_subcategorias(
    categoria_id: Optional[str] = None,
    uid: str = Depends(get_current_user_id),
    cur=Depends(get_db),
):
    return cadastros.listar_subcategorias(cur, uid, categoria_id)


@router.post("/subcategorias", status_code=201)
def criar_subcategoria(body: SubcategoriaIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.criar_subcategoria(cur, uid, body.categoria_id, body.nome)


# ───────────────── Locais ─────────────────
@router.get("/locais")
def listar_locais(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.listar_locais(cur, uid)


@router.post("/locais", status_code=201)
def criar_local(body: NomeIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.criar_local(cur, uid, body.nome)


@router.delete("/locais/{id_}")
def excluir_local(id_: str, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    cadastros.excluir_local(cur, uid, id_)
    return {"ok": True}


# ───────────────── Contas ─────────────────
@router.get("/contas")
def listar_contas(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.listar_contas(cur, uid)


@router.post("/contas", status_code=201)
def criar_conta(body: ContaIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.criar_conta(cur, uid, body.nome, body.tipo)


@router.delete("/contas/{id_}")
def excluir_conta(id_: str, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    cadastros.excluir_conta(cur, uid, id_)
    return {"ok": True}


# ───────────────── Cartoes ─────────────────
@router.get("/cartoes")
def listar_cartoes(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.listar_cartoes(cur, uid)


@router.post("/cartoes", status_code=201)
def criar_cartao(body: CartaoIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return cadastros.criar_cartao(
        cur, uid, body.nome, body.dia_fechamento, body.dia_vencimento, body.bandeira, body.limite
    )


@router.delete("/cartoes/{id_}")
def excluir_cartao(id_: str, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    cadastros.excluir_cartao(cur, uid, id_)
    return {"ok": True}


# ───────────────── Despesas ─────────────────
@router.get("/despesas")
def listar_despesas(
    inicio: Optional[date] = None,
    fim: Optional[date] = None,
    categoria_id: Optional[str] = None,
    limite: int = Query(100, le=500),
    uid: str = Depends(get_current_user_id),
    cur=Depends(get_db),
):
    return despesas.listar_despesas(cur, uid, inicio, fim, categoria_id, limite)


@router.post("/despesas", status_code=201)
def criar_despesa(body: DespesaIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return despesas.criar_despesa(
        cur, uid,
        descricao=body.descricao, valor_total=body.valor_total, data=body.data,
        forma_pagamento=body.forma_pagamento, conta_id=body.conta_id, cartao_id=body.cartao_id,
        num_parcelas=body.num_parcelas, categoria_id=body.categoria_id,
        subcategoria_id=body.subcategoria_id, local_id=body.local_id,
    )


@router.put("/despesas/{id_}")
def editar_despesa(id_: str, body: DespesaEditIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return despesas.editar_despesa(cur, uid, id_, **body.model_dump(exclude_none=True))


@router.delete("/despesas/{id_}")
def excluir_despesa(
    id_: str,
    confirmar: bool = False,
    uid: str = Depends(get_current_user_id),
    cur=Depends(get_db),
):
    despesas.excluir_despesa(cur, uid, id_, confirmar=confirmar)
    return {"ok": True}


# ───────────────── Faturas ─────────────────
@router.get("/faturas")
def proximas_faturas(
    cartao_id: Optional[str] = None,
    uid: str = Depends(get_current_user_id),
    cur=Depends(get_db),
):
    return faturas.proximas_faturas(cur, uid, cartao_id)


@router.get("/faturas/{cartao_id}/{competencia}")
def consultar_fatura(cartao_id: str, competencia: date, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return faturas.consultar_fatura(cur, uid, cartao_id, competencia)


@router.post("/faturas/marcar-paga")
def marcar_fatura_paga(body: MarcarFaturaPagaIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return faturas.marcar_fatura_paga(cur, uid, body.cartao_id, body.competencia)


# ───────────────── Dashboard / Seed ─────────────────
@router.get("/dashboard")
def get_dashboard(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return dashboard.resumo(cur, uid)


@router.post("/seed-categorias")
def seed_categorias(body: SeedIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    """Seed opcional de categorias comuns no primeiro login (decisao 4)."""
    criadas = [cadastros.criar_categoria(cur, uid, nome) for nome in body.categorias]
    return criadas
