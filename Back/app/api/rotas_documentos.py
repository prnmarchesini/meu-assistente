"""Rotas de documentos (Passo 4): upload, busca semantica, garantias, vinculo."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..ia.openai_client import gerar_embedding
from ..ia.pipeline_doc import processar_documento
from ..servicos import documentos as svc_doc
from .auth import get_current_user_id
from .deps import get_db

router = APIRouter(dependencies=[Depends(get_current_user_id)])


class BuscarIn(BaseModel):
    consulta: str
    fornecedor: Optional[str] = None
    tipo_documento: Optional[str] = None
    inicio: Optional[date] = None
    fim: Optional[date] = None


class VincularIn(BaseModel):
    despesa_id: str


@router.post("/documentos/upload", status_code=201)
async def upload_documento(
    file: UploadFile = File(...),
    uid: str = Depends(get_current_user_id),
    cur=Depends(get_db),
):
    conteudo = await file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="arquivo vazio")
    try:
        return processar_documento(cur, uid, conteudo, file.filename or "arquivo", file.content_type)
    except RuntimeError as e:
        # tipicamente SUPABASE_SERVICE_KEY ausente (upload ao Storage)
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/documentos")
def listar_documentos(uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return svc_doc.listar_documentos(cur, uid)


@router.get("/garantias")
def garantias_a_vencer(dias: int = 30, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return svc_doc.garantias_a_vencer(cur, uid, dias)


@router.post("/documentos/buscar")
def buscar_documento(body: BuscarIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    emb = gerar_embedding(body.consulta)
    return svc_doc.buscar_documento(
        cur, uid, emb,
        fornecedor=body.fornecedor, tipo_documento=body.tipo_documento,
        inicio=body.inicio, fim=body.fim,
    )


@router.post("/documentos/{documento_id}/vincular")
def vincular(documento_id: str, body: VincularIn, uid: str = Depends(get_current_user_id), cur=Depends(get_db)):
    return svc_doc.vincular_documento_a_despesa(cur, uid, documento_id, body.despesa_id)
