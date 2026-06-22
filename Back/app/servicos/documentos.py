"""Servico de documentos: persistencia, garantias e busca semantica (pgvector)."""
from datetime import date
from decimal import Decimal

from .comuns import RegraNegocioError


def _vec(embedding) -> str | None:
    if embedding is None:
        return None
    return "[" + ",".join(str(float(x)) for x in embedding) + "]"


def _num(v):
    if v in (None, "", "null"):
        return None
    try:
        return Decimal(str(v))
    except Exception:  # noqa: BLE001
        return None


def criar_documento(
    cur, user_id, bucket, path, *,
    fornecedor=None, valor_total=None, data_documento=None,
    fim_garantia=None, tipo_documento=None, texto_extraido=None, embedding=None,
):
    cur.execute(
        """insert into documentos
           (user_id, bucket, path, fornecedor, valor_total, data_documento,
            fim_garantia, tipo_documento, texto_extraido, embedding)
           values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector) returning *""",
        (
            user_id, bucket, path, fornecedor, _num(valor_total), data_documento or None,
            fim_garantia or None, tipo_documento, texto_extraido, _vec(embedding),
        ),
    )
    return cur.fetchone()


def listar_documentos(cur, user_id, limite=100):
    cur.execute(
        "select * from documentos where user_id=%s order by criado_em desc limit %s",
        (user_id, limite),
    )
    return cur.fetchall()


def garantias_a_vencer(cur, user_id, dias=30):
    cur.execute(
        """select * from documentos
           where user_id=%s and fim_garantia is not null
             and fim_garantia between current_date and current_date + %s
           order by fim_garantia""",
        (user_id, int(dias)),
    )
    return cur.fetchall()


def buscar_documento(
    cur, user_id, embedding_consulta, *,
    fornecedor=None, tipo_documento=None, inicio: date = None, fim: date = None, limite=5,
):
    """Similaridade pgvector + filtros estruturados (decisao 16)."""
    cond = ["user_id=%s", "embedding is not null"]
    params = [user_id]
    if fornecedor:
        cond.append("fornecedor ilike %s")
        params.append(f"%{fornecedor}%")
    if tipo_documento:
        cond.append("tipo_documento=%s")
        params.append(tipo_documento)
    if inicio:
        cond.append("data_documento>=%s")
        params.append(inicio)
    if fim:
        cond.append("data_documento<=%s")
        params.append(fim)
    vec = _vec(embedding_consulta)
    params_final = [vec] + params + [vec, limite]
    cur.execute(
        f"""select id, fornecedor, valor_total, data_documento, fim_garantia,
                   tipo_documento, bucket, path,
                   1 - (embedding <=> %s::vector) as score
            from documentos
            where {' and '.join(cond)}
            order by embedding <=> %s::vector
            limit %s""",
        params_final,
    )
    return cur.fetchall()


def vincular_documento_a_despesa(cur, user_id, documento_id, despesa_id):
    cur.execute(
        "select id from despesas where id=%s and user_id=%s", (despesa_id, user_id)
    )
    if not cur.fetchone():
        raise RegraNegocioError("despesa nao encontrada")
    cur.execute(
        "update documentos set despesa_id=%s where id=%s and user_id=%s returning *",
        (despesa_id, documento_id, user_id),
    )
    doc = cur.fetchone()
    if not doc:
        raise RegraNegocioError("documento nao encontrado")
    return doc
