from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from app.core.config import settings


def _get_psycopg_module():
    try:
        import psycopg  # type: ignore

        return psycopg
    except Exception:
        return None


def pg_enabled() -> bool:
    return bool(settings.db_url and _get_psycopg_module() is not None)


@contextmanager
def pg_cursor() -> Generator[object, None, None]:
    psycopg = _get_psycopg_module()
    if not settings.db_url or psycopg is None:
        raise RuntimeError("postgres not configured")
    with psycopg.connect(settings.db_url) as conn:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
