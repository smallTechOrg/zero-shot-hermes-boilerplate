from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, chat, goal
from app.config import settings

# Import db so dev-time create_all runs on startup/TestClient import.
from app import db as _app_db  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(title="demo-agent")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(goal.router)

    @app.get("/")
    async def root():
        return {"ok": True, "project": "demo-agent"}

    return app


app = create_app()
