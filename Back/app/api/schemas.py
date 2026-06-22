"""Schemas (Pydantic) das requisicoes da API."""
from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class NomeIn(BaseModel):
    nome: str


class SubcategoriaIn(BaseModel):
    categoria_id: str
    nome: str


class ContaIn(BaseModel):
    nome: str
    tipo: Optional[str] = None


class CartaoIn(BaseModel):
    nome: str
    dia_fechamento: int = Field(ge=1, le=31)
    dia_vencimento: int = Field(ge=1, le=31)
    bandeira: Optional[str] = None
    limite: Optional[Decimal] = None


class DespesaIn(BaseModel):
    descricao: str
    valor_total: Decimal
    data: date
    forma_pagamento: Literal["conta", "cartao"]
    conta_id: Optional[str] = None
    cartao_id: Optional[str] = None
    num_parcelas: int = 1
    categoria_id: Optional[str] = None
    subcategoria_id: Optional[str] = None
    local_id: Optional[str] = None


class DespesaEditIn(BaseModel):
    descricao: Optional[str] = None
    valor_total: Optional[Decimal] = None
    data: Optional[date] = None
    forma_pagamento: Optional[Literal["conta", "cartao"]] = None
    conta_id: Optional[str] = None
    cartao_id: Optional[str] = None
    num_parcelas: Optional[int] = None
    categoria_id: Optional[str] = None
    subcategoria_id: Optional[str] = None
    local_id: Optional[str] = None


class MarcarFaturaPagaIn(BaseModel):
    cartao_id: str
    competencia: date


class SeedIn(BaseModel):
    categorias: list[str] = Field(
        default_factory=lambda: ["Mercado", "Transporte", "Saude", "Lazer", "Moradia", "Contas"]
    )
