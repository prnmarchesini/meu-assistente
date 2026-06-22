"""Cliente Supabase usando a SERVICE KEY (Storage / Auth admin).

Atencao: a service key bypassa RLS. Todo acesso a dados de usuario deve sempre
filtrar por user_id no codigo.
"""
from functools import lru_cache

from supabase import Client, create_client

from .config import get_settings


@lru_cache
def get_supabase() -> Client:
    s = get_settings()
    if not (s.supabase_url and s.supabase_service_key):
        raise RuntimeError(
            "SUPABASE_URL e SUPABASE_SERVICE_KEY sao necessarios para o cliente Supabase."
        )
    return create_client(s.supabase_url, s.supabase_service_key)
