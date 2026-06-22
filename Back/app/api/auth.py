"""Validacao do JWT do Supabase.

O projeto usa chaves assimetricas (ES256), entao validamos o token offline com a
chave publica do JWKS — sem segredo, sem chamada de rede por requisicao (o
PyJWKClient cacheia as chaves). O frontend NUNCA envia user_id; ele vem do `sub`
do token verificado.
"""
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from ..core.config import get_settings

_bearer = HTTPBearer(auto_error=True)


@lru_cache
def _jwk_client() -> PyJWKClient:
    s = get_settings()
    if not s.supabase_url:
        raise RuntimeError("SUPABASE_URL nao configurado")
    return PyJWKClient(f"{s.supabase_url}/auth/v1/.well-known/jwks.json")


def get_current_user_id(
    cred: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    token = cred.credentials
    try:
        signing_key = _jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            options={"require": ["sub", "exp"]},
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido ou expirado"
        )
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem sub")
    return uid
