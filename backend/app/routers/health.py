from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "version": "0.1.0"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
