"""Testes de documentos (Passo 4): extracao PDF + pgvector + garantias.

A busca usa vetores one-hot (direcoes distintas) para ser deterministica sem
depender da OpenAI. A integracao real com a OpenAI e validada a parte
(script live), para nao tornar a suite dependente de rede/custo.
"""
from datetime import date, timedelta

import fitz

from app.ia.pipeline_doc import bucket_para, extrair_texto_pdf
from app.servicos import cadastros, despesas
from app.servicos import documentos as svc


def _pdf_com_texto(texto: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), texto)
    conteudo = doc.tobytes()
    doc.close()
    return conteudo


def _onehot(i: int) -> list[float]:
    v = [0.0] * 1536
    v[i] = 1.0
    return v


def test_extrair_texto_pdf():
    pdf = _pdf_com_texto("Mercado Exemplo LTDA - total R$ 200,00")
    texto = extrair_texto_pdf(pdf)
    assert "Mercado Exemplo" in texto


def test_pdf_escaneado_sem_texto_retorna_vazio():
    doc = fitz.open()
    doc.new_page()  # pagina em branco, sem texto
    pdf = doc.tobytes()
    doc.close()
    assert extrair_texto_pdf(pdf) == ""


def test_bucket_roteamento():
    assert bucket_para("application/pdf", "nota.pdf") == "pdfs"
    assert bucket_para("image/jpeg", "foto.jpg") == "imagens"
    assert bucket_para(None, "recibo.PDF") == "pdfs"


def test_criar_e_buscar_por_similaridade(cur, user_id):
    svc.criar_documento(
        cur, user_id, "pdfs", "p/1.pdf", fornecedor="Mercado X",
        valor_total="200.00", tipo_documento="nota_fiscal",
        texto_extraido="compra no mercado", embedding=_onehot(0),
    )
    svc.criar_documento(
        cur, user_id, "pdfs", "p/2.pdf", fornecedor="Posto Y",
        tipo_documento="recibo", texto_extraido="combustivel", embedding=_onehot(5),
    )
    res = svc.buscar_documento(cur, user_id, _onehot(0), limite=5)
    assert len(res) == 2
    assert res[0]["fornecedor"] == "Mercado X"  # vetor mais proximo
    assert res[0]["score"] > res[1]["score"]


def test_busca_com_filtro_de_tipo(cur, user_id):
    svc.criar_documento(cur, user_id, "pdfs", "p/1.pdf", fornecedor="A", tipo_documento="nota_fiscal", embedding=_onehot(0))
    svc.criar_documento(cur, user_id, "pdfs", "p/2.pdf", fornecedor="B", tipo_documento="garantia", embedding=_onehot(0))
    res = svc.buscar_documento(cur, user_id, _onehot(0), tipo_documento="garantia")
    assert res and all(r["tipo_documento"] == "garantia" for r in res)


def test_garantias_a_vencer(cur, user_id):
    hoje = date.today()
    svc.criar_documento(cur, user_id, "pdfs", "g/1.pdf", fim_garantia=hoje + timedelta(days=10), tipo_documento="garantia", embedding=_onehot(0))
    svc.criar_documento(cur, user_id, "pdfs", "g/2.pdf", fim_garantia=hoje + timedelta(days=400), tipo_documento="garantia", embedding=_onehot(1))
    res = svc.garantias_a_vencer(cur, user_id, 30)
    assert len(res) == 1
    assert res[0]["path"] == "g/1.pdf"


def test_vincular_documento_a_despesa(cur, user_id):
    conta = cadastros.criar_conta(cur, user_id, "Carteira")
    d = despesas.criar_despesa(
        cur, user_id, descricao="x", valor_total="10.00", data=date.today(),
        forma_pagamento="conta", conta_id=conta["id"],
    )
    doc = svc.criar_documento(cur, user_id, "pdfs", "p/1.pdf", embedding=_onehot(0))
    r = svc.vincular_documento_a_despesa(cur, user_id, doc["id"], d["despesa"]["id"])
    assert r["despesa_id"] == d["despesa"]["id"]
