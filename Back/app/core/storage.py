"""Acesso ao Supabase Storage via API REST.

Usamos httpx direto (em vez do supabase-py) porque a lib nao lida bem com o novo
formato de chave (sb_secret_...). A service key bypassa RLS — uso server-side apenas.
"""
import httpx

from .config import get_settings


def _cfg():
    s = get_settings()
    if not (s.supabase_url and s.supabase_service_key):
        raise RuntimeError("SUPABASE_URL e SUPABASE_SERVICE_KEY sao necessarios para o Storage")
    return s.supabase_url, s.supabase_service_key


def _headers(content_type: str | None = None) -> dict:
    _, key = _cfg()
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    if content_type:
        h["Content-Type"] = content_type
    return h


def upload(bucket: str, path: str, conteudo: bytes, content_type: str = "application/octet-stream") -> str:
    url, _ = _cfg()
    r = httpx.post(
        f"{url}/storage/v1/object/{bucket}/{path}",
        headers=_headers(content_type), content=conteudo, timeout=60,
    )
    r.raise_for_status()
    return path


def remover(bucket: str, path: str):
    url, _ = _cfg()
    httpx.request(
        "DELETE", f"{url}/storage/v1/object/{bucket}/{path}", headers=_headers(), timeout=30
    )
