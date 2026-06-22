"""Catalogo de ferramentas do orquestrador de IA.

Cada tool e um inviolucro fino sobre os servicos do Passo 2/4. O LLM trabalha com
NOMES (categoria, cartao...); a tool resolve para ids. O user_id e SEMPRE injetado
pelo orquestrador, nunca fornecido pelo modelo. Nenhum calculo e feito pelo LLM.
"""
from datetime import date

from ..servicos import cadastros, despesas, documentos, faturas, relatorios
from ..servicos.comuns import RegraNegocioError
from .openai_client import gerar_embedding


def _data(s) -> date:
    if isinstance(s, date):
        return s
    return date.fromisoformat(str(s))


def _resolver_cartao(cur, user_id, nome):
    for c in cadastros.listar_cartoes(cur, user_id):
        if c["nome"].lower() == str(nome).strip().lower():
            return c
    raise RegraNegocioError(f"cartao '{nome}' nao encontrado; cadastre-o primeiro")


# ───────────────── Escrita ─────────────────
def criar_categoria(cur, user_id, nome):
    return cadastros.criar_categoria(cur, user_id, nome)


def criar_subcategoria(cur, user_id, categoria, nome):
    cat = cadastros.criar_categoria(cur, user_id, categoria)
    return cadastros.criar_subcategoria(cur, user_id, cat["id"], nome)


def criar_local(cur, user_id, nome):
    return cadastros.criar_local(cur, user_id, nome)


def criar_conta(cur, user_id, nome, tipo=None):
    return cadastros.criar_conta(cur, user_id, nome, tipo)


def cadastrar_cartao(cur, user_id, nome, dia_fechamento, dia_vencimento, bandeira=None, limite=None):
    return cadastros.criar_cartao(cur, user_id, nome, dia_fechamento, dia_vencimento, bandeira, limite)


def criar_despesa(
    cur, user_id, descricao, valor, data, forma_pagamento,
    conta=None, cartao=None, num_parcelas=1, categoria=None, subcategoria=None, local=None,
):
    categoria_id = cadastros.criar_categoria(cur, user_id, categoria)["id"] if categoria else None
    subcategoria_id = None
    if subcategoria and categoria:
        subcategoria_id = cadastros.criar_subcategoria(cur, user_id, categoria_id, subcategoria)["id"]
    local_id = cadastros.criar_local(cur, user_id, local)["id"] if local else None

    conta_id = cartao_id = None
    if forma_pagamento == "conta":
        conta_id = cadastros.criar_conta(cur, user_id, conta)["id"] if conta else None
    else:
        cartao_id = _resolver_cartao(cur, user_id, cartao)["id"]

    return despesas.criar_despesa(
        cur, user_id, descricao=descricao, valor_total=valor, data=_data(data),
        forma_pagamento=forma_pagamento, conta_id=conta_id, cartao_id=cartao_id,
        num_parcelas=int(num_parcelas or 1), categoria_id=categoria_id,
        subcategoria_id=subcategoria_id, local_id=local_id,
    )


def marcar_fatura_paga(cur, user_id, cartao, competencia):
    c = _resolver_cartao(cur, user_id, cartao)
    return faturas.marcar_fatura_paga(cur, user_id, c["id"], _data(competencia))


def vincular_documento_a_despesa(cur, user_id, documento_id, despesa_id):
    return documentos.vincular_documento_a_despesa(cur, user_id, documento_id, despesa_id)


# ───────────────── Leitura ─────────────────
def consultar_fatura(cur, user_id, cartao, competencia):
    c = _resolver_cartao(cur, user_id, cartao)
    return faturas.consultar_fatura(cur, user_id, c["id"], _data(competencia))


def proximas_faturas(cur, user_id, cartao=None):
    cartao_id = _resolver_cartao(cur, user_id, cartao)["id"] if cartao else None
    return faturas.proximas_faturas(cur, user_id, cartao_id)


def total_por_periodo(cur, user_id, inicio, fim, agrupar_por=None):
    if agrupar_por == "categoria":
        return relatorios.total_por_categoria(cur, user_id, _data(inicio), _data(fim))
    return relatorios.total_por_periodo(cur, user_id, _data(inicio), _data(fim))


def total_por_categoria(cur, user_id, inicio=None, fim=None):
    if not (inicio and fim):
        inicio, fim = relatorios.periodo_mes_atual()
    return relatorios.total_por_categoria(cur, user_id, _data(inicio), _data(fim))


def garantias_a_vencer(cur, user_id, dias=30):
    return documentos.garantias_a_vencer(cur, user_id, int(dias))


def buscar_documento(cur, user_id, consulta):
    return documentos.buscar_documento(cur, user_id, gerar_embedding(consulta))


def listar_despesas(cur, user_id, inicio=None, fim=None, categoria=None):
    categoria_id = None
    if categoria:
        for c in cadastros.listar_categorias(cur, user_id):
            if c["nome"].lower() == str(categoria).strip().lower():
                categoria_id = c["id"]
    return despesas.listar_despesas(
        cur, user_id, _data(inicio) if inicio else None, _data(fim) if fim else None, categoria_id
    )


# ───────────────── Registro (dispatch + spec p/ o LLM) ─────────────────
DISPATCH = {
    "criar_categoria": criar_categoria,
    "criar_subcategoria": criar_subcategoria,
    "criar_local": criar_local,
    "criar_conta": criar_conta,
    "cadastrar_cartao": cadastrar_cartao,
    "criar_despesa": criar_despesa,
    "marcar_fatura_paga": marcar_fatura_paga,
    "vincular_documento_a_despesa": vincular_documento_a_despesa,
    "consultar_fatura": consultar_fatura,
    "proximas_faturas": proximas_faturas,
    "total_por_periodo": total_por_periodo,
    "total_por_categoria": total_por_categoria,
    "garantias_a_vencer": garantias_a_vencer,
    "buscar_documento": buscar_documento,
    "listar_despesas": listar_despesas,
}

FERRAMENTAS_ESCRITA = {
    "criar_categoria", "criar_subcategoria", "criar_local", "criar_conta",
    "cadastrar_cartao", "criar_despesa", "marcar_fatura_paga",
    "vincular_documento_a_despesa",
}


def _f(nome, descricao, propriedades, obrigatorios):
    return {
        "type": "function",
        "function": {
            "name": nome,
            "description": descricao,
            "parameters": {
                "type": "object",
                "properties": propriedades,
                "required": obrigatorios,
            },
        },
    }


_STR = {"type": "string"}
_NUM = {"type": "number"}
_INT = {"type": "integer"}

TOOLS_SPEC = [
    _f("criar_categoria", "Cria uma categoria de despesa.", {"nome": _STR}, ["nome"]),
    _f("criar_subcategoria", "Cria subcategoria dentro de uma categoria.",
       {"categoria": _STR, "nome": _STR}, ["categoria", "nome"]),
    _f("criar_local", "Cria um local de compra.", {"nome": _STR}, ["nome"]),
    _f("criar_conta", "Cria uma conta (corrente, poupanca, dinheiro).",
       {"nome": _STR, "tipo": _STR}, ["nome"]),
    _f("cadastrar_cartao", "Cadastra um cartao de credito.",
       {"nome": _STR, "dia_fechamento": _INT, "dia_vencimento": _INT, "bandeira": _STR, "limite": _NUM},
       ["nome", "dia_fechamento", "dia_vencimento"]),
    _f("criar_despesa",
       "Cria uma despesa. forma_pagamento 'conta' usa 'conta'; 'cartao' usa 'cartao' e 'num_parcelas'. data em YYYY-MM-DD.",
       {"descricao": _STR, "valor": _NUM, "data": _STR,
        "forma_pagamento": {"type": "string", "enum": ["conta", "cartao"]},
        "conta": _STR, "cartao": _STR, "num_parcelas": _INT,
        "categoria": _STR, "subcategoria": _STR, "local": _STR},
       ["descricao", "valor", "data", "forma_pagamento"]),
    _f("marcar_fatura_paga", "Marca a fatura de um cartao como paga. competencia em YYYY-MM-01.",
       {"cartao": _STR, "competencia": _STR}, ["cartao", "competencia"]),
    _f("vincular_documento_a_despesa", "Vincula um documento a uma despesa.",
       {"documento_id": _STR, "despesa_id": _STR}, ["documento_id", "despesa_id"]),
    _f("consultar_fatura", "Consulta a fatura de um cartao numa competencia (YYYY-MM-01).",
       {"cartao": _STR, "competencia": _STR}, ["cartao", "competencia"]),
    _f("proximas_faturas", "Lista as proximas faturas a vencer (opcionalmente de um cartao).",
       {"cartao": _STR}, []),
    _f("total_por_periodo", "Total gasto entre inicio e fim (YYYY-MM-DD). agrupar_por='categoria' opcional.",
       {"inicio": _STR, "fim": _STR, "agrupar_por": _STR}, ["inicio", "fim"]),
    _f("total_por_categoria", "Total por categoria (periodo opcional; padrao mes atual).",
       {"inicio": _STR, "fim": _STR}, []),
    _f("garantias_a_vencer", "Lista garantias vencendo nos proximos N dias (padrao 30).",
       {"dias": _INT}, []),
    _f("buscar_documento", "Busca semantica de documentos por descricao do conteudo.",
       {"consulta": _STR}, ["consulta"]),
    _f("listar_despesas", "Lista despesas (filtros opcionais: inicio, fim, categoria).",
       {"inicio": _STR, "fim": _STR, "categoria": _STR}, []),
]
