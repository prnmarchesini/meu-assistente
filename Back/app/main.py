"""Aplicacao FastAPI — ponto de entrada."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.rotas import router as api_router
from .core.db import check_connection
from .servicos.comuns import RegraNegocioError

app = FastAPI(title="Controle de Gastos API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringido no Passo 7 (producao)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RegraNegocioError)
async def regra_negocio_handler(_: Request, exc: RegraNegocioError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health():
    """Testa a conexao com o Supabase (Passo 1)."""
    try:
        ok = check_connection()
        return {"status": "ok" if ok else "degraded", "supabase": ok}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "supabase": False, "detail": str(exc)[:200]}


app.include_router(api_router)
