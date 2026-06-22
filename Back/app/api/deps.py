"""Dependencias da API."""
from psycopg2.extras import RealDictCursor

from ..core.db import get_connection


def get_db():
    """Fornece um cursor por requisicao; commit no sucesso, rollback no erro."""
    with get_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
