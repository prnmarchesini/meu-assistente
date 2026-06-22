"""Aplicacao FastAPI — ponto de entrada."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.db import check_connection

app = FastAPI(title="Controle de Gastos API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringido no Passo 7 (producao)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Testa a conexao com o Supabase (Passo 1)."""
    try:
        ok = check_connection()
        return {"status": "ok" if ok else "degraded", "supabase": ok}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "supabase": False, "detail": str(exc)[:200]}
