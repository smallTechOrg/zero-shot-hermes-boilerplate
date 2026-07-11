import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "", 1)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

_connect_args: dict[str, object] = {"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    # WAL avoids reader/writer blocking; busy_timeout prevents "database is locked" hangs
    # under concurrent requests (uvicorn threadpool) without needing a separate server.
    _connect_args["timeout"] = 30

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
    pool_pre_ping=True,
)


def _enable_wal() -> None:
    if DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
                conn.exec_driver_sql("PRAGMA busy_timeout=30000;")
        except Exception:
            pass


_enable_wal()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Lazy import avoids circular imports and guarantees models are registered
# before create_all runs.
def _init_models() -> None:
    from app.models import Run  # noqa: F401
    Base.metadata.create_all(bind=engine)


_init_models()
