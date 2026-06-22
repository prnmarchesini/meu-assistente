"""Logging estruturado (JSON) sem vazar segredos nem dados sensiveis."""
import json
import logging
import sys

_SENSIVEIS = ("authorization", "token", "secret", "api_key", "apikey", "password", "senha")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "nivel": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        extra = getattr(record, "contexto", None)
        if isinstance(extra, dict):
            base.update({k: v for k, v in extra.items() if not _e_sensivel(k)})
        return json.dumps(base, ensure_ascii=False, default=str)


def _e_sensivel(chave: str) -> bool:
    c = chave.lower()
    return any(s in c for s in _SENSIVEIS)


def configurar_logging(nivel=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(nivel)
    # Reduz verbosidade de libs ruidosas.
    for ruidoso in ("httpx", "httpcore", "openai"):
        logging.getLogger(ruidoso).setLevel(logging.WARNING)
