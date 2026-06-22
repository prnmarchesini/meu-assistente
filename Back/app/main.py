"""Aplicacao FastAPI — ponto de entrada."""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.rotas import router as api_router
from .api.rotas_chat import router as chat_router
from .api.rotas_documentos import router as documentos_router
from .api.rotas_telegram import router as telegram_router
from .core.config import get_settings
from .core.db import check_connection
from .core.logging_config import configurar_logging
from .servicos.comuns import RegraNegocioError

configurar_logging()
log = logging.getLogger("app")
_settings = get_settings()

app = FastAPI(title="Controle de Gastos API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.lista_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requisicoes(request: Request, call_next):
    inicio = time.time()
    resposta = await call_next(request)
    dur_ms = round((time.time() - inicio) * 1000)
    log.info(
        "request",
        extra={"contexto": {"metodo": request.method, "rota": request.url.path,
                            "status": resposta.status_code, "ms": dur_ms}},
    )
    return resposta


@app.exception_handler(RegraNegocioError)
async def regra_negocio_handler(_: Request, exc: RegraNegocioError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health():
    """Testa a conexao com o Supabase."""
    try:
        ok = check_connection()
        return {"status": "ok" if ok else "degraded", "supabase": ok}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "supabase": False, "detail": str(exc)[:200]}


app.include_router(api_router)
app.include_router(documentos_router)
app.include_router(chat_router)
app.include_router(telegram_router)
