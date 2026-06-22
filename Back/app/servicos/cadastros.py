"""CRUD dos cadastros: categorias, subcategorias, locais, contas, cartoes.

Todas as funcoes recebem o cursor como dependencia e filtram por user_id.
Nomes sao normalizados; duplicatas case-insensitive retornam o registro
existente (get-or-create) — decisao 18.
"""
from .comuns import RegraNegocioError, normalizar_nome

# Tabelas simples baseadas em (user_id, nome). Allowlist interna (nao vem do usuario).
_TABELAS_NOME = {"categorias", "locais", "contas"}


def _get_or_create_por_nome(cur, tabela, user_id, nome, extras=None):
    if tabela not in _TABELAS_NOME:
        raise ValueError(f"tabela invalida: {tabela}")
    nome = normalizar_nome(nome)
    cur.execute(
        f"select * from {tabela} where user_id=%s and lower(nome)=lower(%s)",
        (user_id, nome),
    )
    existente = cur.fetchone()
    if existente:
        return existente
    cols = ["user_id", "nome"]
    vals = [user_id, nome]
    for k, v in (extras or {}).items():
        cols.append(k)
        vals.append(v)
    ph = ",".join(["%s"] * len(vals))
    cur.execute(f"insert into {tabela} ({','.join(cols)}) values ({ph}) returning *", vals)
    return cur.fetchone()


def _listar(cur, tabela, user_id):
    cur.execute(f"select * from {tabela} where user_id=%s order by lower(nome)", (user_id,))
    return cur.fetchall()


def _excluir(cur, tabela, user_id, id_):
    cur.execute(f"delete from {tabela} where id=%s and user_id=%s returning id", (id_, user_id))
    if not cur.fetchone():
        raise RegraNegocioError("registro nao encontrado")
    return True


# ── Categorias ──
def criar_categoria(cur, user_id, nome):
    return _get_or_create_por_nome(cur, "categorias", user_id, nome)


def listar_categorias(cur, user_id):
    return _listar(cur, "categorias", user_id)


def excluir_categoria(cur, user_id, id_):
    return _excluir(cur, "categorias", user_id, id_)


# ── Subcategorias ──
def criar_subcategoria(cur, user_id, categoria_id, nome):
    nome = normalizar_nome(nome)
    cur.execute(
        "select id from categorias where id=%s and user_id=%s", (categoria_id, user_id)
    )
    if not cur.fetchone():
        raise RegraNegocioError("categoria nao encontrada")
    cur.execute(
        """select * from subcategorias
           where user_id=%s and categoria_id=%s and lower(nome)=lower(%s)""",
        (user_id, categoria_id, nome),
    )
    existente = cur.fetchone()
    if existente:
        return existente
    cur.execute(
        """insert into subcategorias (user_id, categoria_id, nome)
           values (%s,%s,%s) returning *""",
        (user_id, categoria_id, nome),
    )
    return cur.fetchone()


def listar_subcategorias(cur, user_id, categoria_id=None):
    if categoria_id:
        cur.execute(
            "select * from subcategorias where user_id=%s and categoria_id=%s order by lower(nome)",
            (user_id, categoria_id),
        )
    else:
        cur.execute(
            "select * from subcategorias where user_id=%s order by lower(nome)", (user_id,)
        )
    return cur.fetchall()


# ── Locais ──
def criar_local(cur, user_id, nome):
    return _get_or_create_por_nome(cur, "locais", user_id, nome)


def listar_locais(cur, user_id):
    return _listar(cur, "locais", user_id)


def excluir_local(cur, user_id, id_):
    return _excluir(cur, "locais", user_id, id_)


# ── Contas ──
def criar_conta(cur, user_id, nome, tipo=None):
    return _get_or_create_por_nome(cur, "contas", user_id, nome, extras={"tipo": tipo})


def listar_contas(cur, user_id):
    return _listar(cur, "contas", user_id)


def excluir_conta(cur, user_id, id_):
    return _excluir(cur, "contas", user_id, id_)


# ── Cartoes ──
def _valida_dia(dia, campo):
    if dia is None or not (1 <= int(dia) <= 31):
        raise RegraNegocioError(f"{campo} deve estar entre 1 e 31")
    return int(dia)


def criar_cartao(cur, user_id, nome, dia_fechamento, dia_vencimento, bandeira=None, limite=None):
    nome = normalizar_nome(nome)
    dia_fechamento = _valida_dia(dia_fechamento, "dia_fechamento")
    dia_vencimento = _valida_dia(dia_vencimento, "dia_vencimento")
    cur.execute(
        "select * from cartoes where user_id=%s and lower(nome)=lower(%s)", (user_id, nome)
    )
    existente = cur.fetchone()
    if existente:
        return existente
    cur.execute(
        """insert into cartoes (user_id, nome, dia_fechamento, dia_vencimento, bandeira, limite)
           values (%s,%s,%s,%s,%s,%s) returning *""",
        (user_id, nome, dia_fechamento, dia_vencimento, bandeira, limite),
    )
    return cur.fetchone()


def listar_cartoes(cur, user_id):
    return _listar(cur, "cartoes", user_id)


def excluir_cartao(cur, user_id, id_):
    return _excluir(cur, "cartoes", user_id, id_)
