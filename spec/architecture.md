# Architecture — `scaffold-agent`

> Single source of truth for the runnable scaffold. This repo **is** the scaffold — there is no generator step; the code in `backend/` and `frontend/` runs as-is.

---

## System Overview

This repo is a **runnable multi-agent hackathon starter-kit**. You clone it, install deps, and run it. No `bootstrap.py`, no `templates/` — the agent code lives directly in the repo. Copy `backend/`, `frontend/`, `deploy/`, `capabilities/` into a new repo and rename `demo-agent` → your project to reuse it as a boilerplate.

The default agent is a minimal but real supervisor/worker graph:
- **supervisor** decides routing,
- **worker** calls the configured LLM (OpenAI-compatible endpoint) when a key is set, otherwise returns a `[stub]` reply,
- **handle_error** terminates with a user-facing message on failure.

The goal loop (`/goals`) lets automation drive the agent through multiple steps without manual intervention.

## Component Map

```
repo root                          ← repo IS the agent project
├── backend/                       ← FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── main.py                ← create_app() factory, CORS, routers
│   │   ├── config.py              ← pydantic-settings; LLM provider/key/base_url/model
│   │   ├── db.py                  ← engine + SessionLocal + Base; create_all on import
│   │   ├── models.py              ← Run, Goal ORM models
│   │   ├── agent.py               ← supervisor/worker/handle_error graph + run_graph()
│   │   ├── capabilities.py        ← loads capabilities/*.md into a route table
│   │   └── routers/
│   │       ├── health.py          ← GET /health (DB-backed liveness)
│   │       ├── chat.py            ← POST /api/chat, GET /api/runs, /api/runs/{id}
│   │       └── goal.py            ← POST/GET /goals, /goals/{id}/run, /goals/{id}/next
│   ├── alembic/                   ← migration tooling (env.py wires Base.metadata)
│   ├── alembic.ini
│   ├── tests/                     ← pytest unit tests (TestClient)
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                      ← React 18 + Vite 5 + TypeScript + Tailwind
│   ├── src/App.tsx                ← chat UI; calls /api/chat via fetch
│   └── package.json
├── capabilities/                  ← one .md file per capability (loaded at runtime)
├── deploy/                        ← GCP VM path: Dockerfile, startup script, terraform, cloudbuild
├── evals/                         ← behaviour evals (stub) + 1 live-gated test
├── harness/                       ← Hermes-native skill/agent/pattern stubs (methodology)
├── spec/                          ← this spec (single source of truth)
├── docker-compose.yml             ← backend :8000 + frontend :5173
├── Dockerfile.backend             ← used by compose
└── README.md
```

## Layers

| Layer | Responsibility |
|-------|----------------|
| API | FastAPI routers expose `/health`, `/api/chat`, `/api/runs`, and the `/goals` loop. |
| Agent | `app/agent.py` supervisor→worker graph; live LLM when a key is present, else `[stub]`. |
| Capabilities | `capabilities/*.md` describe discrete capabilities; the supervisor can route by name. |
| Data | SQLAlchemy 2.0 core + SQLite in dev. Swap to Postgres via `DATABASE_URL` (no code change needed for the ORM). |
| Frontend | Vite + React + TypeScript. Calls `/api/chat` with `fetch`. |
| Ops | Docker Compose binds backend `:8000` and frontend dev server `:5173`. |

## Data Flow

1. User POSTs `{messages:[...]}` to `/api/chat`.
2. FastAPI validates with Pydantic (`ChatRequest`).
3. `run_graph()` runs the supervisor, then the worker:
   - Key present (`LLM_API_KEY` or provider key): POSTs to the configured OpenAI-compatible `/v1/chat/completions` endpoint.
   - No key: returns a `[stub]` reply echoing the user message.
4. Response returned as `{"reply": "...", "run_id": N}`; a `Run` row is persisted.
5. Frontend appends user bubble and assistant bubble.

## External Dependencies

| Dependency | Purpose | Failure Mode |
|------------|---------|--------------|
| LLM API (OpenAI-compatible) | Live agent responses (optional) | Stub path used automatically; service stays up. |
| Docker | Local dev via Compose | Run backend/frontend manually: `uvicorn` + `npm run dev`. |
| npm | Frontend build | Fails clearly at `npm install`. |
| pip / venv | Python deps | Fails clearly at install step. |

## Stack

- **Agent framework:** hand-rolled supervisor/worker graph (no LangGraph/CrewAI/AutoGen dependency — keeps the install surface small). Extensible to multi-worker, planning, reflection.
- **LLM provider + model:** configurable via `LLM_PROVIDER` (`gemini` | `openai`), `LLM_API_KEY` / `GEMINI_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`. Default: Gemini `gemini-1.5-flash` via the OpenAI-compatible endpoint.
- **Backend:** FastAPI + Uvicorn + SQLAlchemy 2.0 + Alembic.
- **Database:** SQLite in dev (`DATABASE_URL`); Postgres-ready via the same `DATABASE_URL` switch (no code change for the ORM).
- **Frontend:** React 18 + Vite 5 + TypeScript + Tailwind `frontend/` (not `web/`).
- **Packaging:** `requirements.txt` + venv in `backend/`; `package.json` in `frontend/`.
- **Agent harness:** `harness/skills/<slug>/SKILL.md` + `harness/agents/*.md` stubs for orchestrator/worker/qa patterns (methodology, not required to run the scaffold).
- **Protocol surfaces:** not included in the base scaffold (add MCP/A2A when your agent needs them).

| Key library | Version | Purpose |
|-------------|---------|---------|
| fastapi | >=0.111 | API |
| uvicorn[standard] | >=0.30 | ASGI server |
| sqlalchemy | >=2.0 | ORM |
| alembic | >=1.13 | Migrations |
| pydantic-settings | >=2.4 | Config |
| httpx | >=0.27 | LLM calls |
| react | 18 | Frontend UI |
| vite | 5 | Frontend tooling |

## Deployment Model

- **Local dev:** `docker compose up --build` binds `:8000` and `:5173`. Or run manually: `uvicorn app.main:app --port 8000` + `npm run dev`.
- **GCP VM:** `deploy/` has a multi-stage `Dockerfile`, `gcp-vm-startup.sh`, `terraform/main.tf`, and `cloudbuild.yaml`. Single VM runs the backend image; the frontend is served via the dev server or built statically.
- **Migration:** tables are created via `Base.metadata.create_all` on import (dev). For prod use Alembic: `alembic upgrade head`.
