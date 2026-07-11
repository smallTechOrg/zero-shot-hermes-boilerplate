# Zero-Shot Hermes Harness — Entry Point

This is a **working multi-agent hackathon boilerplate** (not a generator). The runnable code
lives directly in the repo. FastAPI + React/Vite + SQLite, with a Hermes goal loop.

## What this repo is

A starter-kit for building agents **spec-first**. One person with an idea and one API key can
get a real, production-shaped agent running in 20–60 minutes. The code is conventional and
reviewable — no codegen step required.

## Layout (actual)

```
backend/            FastAPI app (the agent)
  app/main.py       FastAPI app + routers
  app/agent.py      supervisor/worker graph; calls Gemini when LLM_API_KEY set
  app/config.py     settings (reads .env)
  app/db.py         SQLAlchemy engine + SQLite (WAL mode)
  app/models.py     Run, Goal tables
  app/routers/      health, chat, goal
  tests/            backend unit tests
frontend/           React + TS + Vite + Tailwind chat UI
deploy/             GCP VM path (Dockerfile, startup script, terraform, cloudbuild)
capabilities/       one-file-per-capability plugin convention
harness/            Hermes skill/agent/pattern stubs (how to extend the kit)
spec/              product spec (single source of truth)
evals/             behaviour + live evals (pytest)
```

## First action every session

1. Read `harness/rules/ai-agents.md` (mandatory rules).
2. Read `spec/roadmap.md` — if it still has `<!-- FILL IN -->`, the spec is not ready.
3. Read the rest of `spec/` before touching application code.

## Run it

```bash
# backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# frontend (separate terminal)
cd frontend && npm install && npm run dev

# evals
cd backend && .venv/bin/python -m pytest ../evals/ -v
```

## Go live with a key

Copy `.env.example` → `.env` and set `GEMINI_API_KEY`. Restart the backend.
`POST /api/chat` will then call Gemini (OpenAI-compatible endpoint) instead of returning `[stub]`.

## Key rules (summary — full rules in harness/rules/ai-agents.md)

- Spec is the source of truth; when spec and code disagree, the spec wins.
- Never write application code before reading the full spec.
- Tests and evals run against the real LLM/API using keys from `.env` (live eval auto-skips without a key).
- Commit every logical unit of work; never leave the tree dirty.
- `.env` is never committed.
