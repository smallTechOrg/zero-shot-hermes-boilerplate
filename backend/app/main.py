from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, chat, goal, capabilities
from app.config import settings
from app import capabilities as _capabilities

# Import db so dev-time create_all runs on startup/TestClient import.
from app import db as _app_db  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(title="demo-agent")
    # Load capability docs once at startup.
    _capabilities.load_capabilities()

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
    app.include_router(capabilities.router)

    @app.get("/")
    async def root():
        return {"ok": True, "project": "demo-agent"}

    return app


app = create_app()
