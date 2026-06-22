"""Pipeline de documentos: extracao -> estruturacao -> embedding -> persistencia.

`analisar_conteudo` faz extracao/estruturacao/embedding (sem banco nem Storage) e
e a parte testavel isoladamente. `processar_documento` adiciona upload ao Storage
e persistencia, e propoe uma despesa (NAO salva sozinho — decisao 5).
"""
import json
import uuid

import fitz  # PyMuPDF

from ..core import storage
from ..servicos import documentos as svc_doc
from .openai_client import estruturar_imagem, estruturar_texto, gerar_embedding


def extrair_texto_pdf(conteudo: bytes) -> str:
    doc = fitz.open(stream=conteudo, filetype="pdf")
    try:
        return "\n".join(p.get_text() for p in doc).strip()
    finally:
        doc.close()


def _ocr_pdf_escaneado(conteudo: bytes) -> dict:
    """PDF sem texto nativo: rasteriza a 1a pagina e manda pro vision."""
    doc = fitz.open(stream=conteudo, filetype="pdf")
    try:
        png = doc[0].get_pixmap(dpi=200).tobytes("png")
    finally:
        doc.close()
    return estruturar_imagem(png, "image/png")


def bucket_para(content_type: str, filename: str) -> str:
    if (content_type or "").lower() == "application/pdf" or filename.lower().endswith(".pdf"):
        return "pdfs"
    return "imagens"


def analisar_conteudo(conteudo: bytes, filename: str, content_type: str) -> dict:
    """Extrai texto, estrutura os campos e gera o embedding. Sem banco/Storage."""
    bucket = bucket_para(content_type, filename)
    texto = ""
    if bucket == "pdfs":
        texto = extrair_texto_pdf(conteudo)
        dados = estruturar_texto(texto) if texto else _ocr_pdf_escaneado(conteudo)
    else:
        dados = estruturar_imagem(conteudo, content_type or "image/jpeg")

    base = texto or json.dumps(dados, ensure_ascii=False)
    embedding = gerar_embedding(base)
    return {"bucket": bucket, "texto": texto, "dados": dados, "embedding": embedding}


def _subir_storage(user_id, bucket, conteudo, filename, content_type) -> str:
    path = f"{user_id}/{uuid.uuid4()}/{filename}"
    return storage.upload(bucket, path, conteudo, content_type or "application/octet-stream")


def processar_documento(cur, user_id, conteudo: bytes, filename: str, content_type: str) -> dict:
    analise = analisar_conteudo(conteudo, filename, content_type)
    path = _subir_storage(user_id, analise["bucket"], conteudo, filename, content_type)

    dados = analise["dados"]
    doc = svc_doc.criar_documento(
        cur, user_id, analise["bucket"], path,
        fornecedor=dados.get("fornecedor"), valor_total=dados.get("valor_total"),
        data_documento=dados.get("data_documento"), fim_garantia=dados.get("fim_garantia"),
        tipo_documento=dados.get("tipo_documento"), texto_extraido=analise["texto"],
        embedding=analise["embedding"],
    )
    # Sugestao de despesa pre-preenchida — so persiste apos confirmacao (decisoes 5, 6).
    sugestao = {
        "descricao": dados.get("fornecedor") or "Documento",
        "valor_total": dados.get("valor_total"),
        "data": dados.get("data_documento"),
        "documento_id": doc["id"],
    }
    return {"documento": doc, "sugestao_despesa": sugestao}
