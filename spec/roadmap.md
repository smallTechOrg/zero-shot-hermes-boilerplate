# Roadmap — `scaffold-agent`

> Filled by the spec-writer sub-agent. Every field is authoritative. Tests run against real behavior on the tested path.

---

## What This Repo Does

This repo is the **scaffold product**: a self-contained, runnable hackathon starter-kit for building AI agents. You clone it and run it directly — there is no generator step. The agent code (`backend/app/`) and `frontend/` run as-is.

It is optimized for the fastest cycle: target **20–60 minutes** from idea to a runnable agent that can be immediately hacked into a professional agent, including complex multi-agent workflows and product launches. Reuse it as a boilerplate by copying `backend/`, `frontend/`, `deploy/`, `capabilities/` into a new repo and renaming `demo-agent` → your project.

## Who Uses It

Engineers in a hackathon, greenfield sprint, or weekend agent build who want the strongest starting point: multi-agent architecture (supervisor/worker), web UI, capability-plugin convention, Hermes-native packaging, and deploy-ready Docker/GCP paths — without manually wiring ports, sessions, persistence, or frontend shells.

## Core Problem Being Solved

Most scaffold repos are either empty boilerplate or opinionated generators that lock you into one app shape. This repo gives you a **runnable** agent scaffold you can open in Claude Code, Hermes, Docker, or deploy to a GCP VM, then extend in place. It is built to support idea-to-running-app times of 20–60 minutes for hackathon/sprint ideas that can grow into full products.

## Success Criteria

- `git clone` + install + `docker compose up --build` serves backend + web.
- `GET /health` returns `{"status":"ok"}`.
- React loads and calls backend successfully via `/api/chat`.
- A real LLM key optionally enables live agent responses; without it, the supervisor stub behaves predictably (`[stub]` prefix).
- `backend/tests/` pass; `evals/` pass in stub mode (live test skips without a key).
- CI (`.github/workflows/ci.yml`) runs tests + frontend build on every push/PR.
- `deploy/` paths produce a runnable GCP VM.

## What This Repo Does NOT Do

- It does not implement user-facing application logic beyond the minimal agent stub.
- It does not include a project generator (`bootstrap.py` / `templates/`) — the code is the template.
- It does not include LangGraph, CrewAI, or AutoGen runtime in the base template (the supervisor/worker graph is hand-rolled to keep the dependency surface small).
- It does not auto-deploy; deployment instructions are provided for GCP VM.

## Key Constraints

- The repo root IS the agent project (no `<agent-slug>/` subdirectory).
- Python: `venv` + `requirements.txt` (no `uv` required; `uv` works too).
- npm for the frontend (no pnpm).
- SQLite in dev; Postgres-ready via `DATABASE_URL`.
- LLM keys via `.env`; no secrets committed.

## Phases of Development

> Each phase is one human-testable increment, behind a testing gate. Commands are exact.

### Phase 1 — Runnable Scaffold (this handoff)

- **Goal:** A runnable FastAPI + React + SQLite agent with a supervisor/worker graph.
- **Shipped slices:**
  - `slice-backend` — FastAPI app: `main.py`, `config.py`, `db.py`, `models.py`, `agent.py`, routers (`health`, `chat`, `goal`).
  - `slice-frontend` — Vite + React + TS chat UI, Tailwind, fetch wiring to `/api/chat`.
  - `slice-ops` — `docker-compose.yml`, `Dockerfile.backend`, `frontend/Dockerfile.frontend`, `.env.example`, `README.md`.
  - `slice-ci` — `.github/workflows/ci.yml` (backend tests, evals, frontend build, deploy-image build).
- **Gate command:** `cd backend && .venv/bin/python -m pytest tests -v` and `cd frontend && npm run build`.
- **How the user tests it:**
  1. `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  2. `uvicorn app.main:app --port 8000` (or `docker compose up --build`)
  3. `curl http://localhost:8000/health` → `{"status":"ok"}`
  4. Open `http://localhost:5173`; chat input calls `/api/chat`.

### Phase 2 — Agent Slot + Persistence (shipped)

- **Goal:** Supervisor/worker graph with live LLM when env set, run persistence, and a Hermes goal loop.
- **Shipped slices:**
  - `slice-agent-graph` — `app/agent.py` supervisor→worker flow; live LLM when key set, else `[stub]`.
  - `slice-persistence` — `Run` table; `/api/chat` writes a run receipt + `run_id`.
  - `slice-runs-api` — `/api/runs`, `/api/runs/{run_id}`.
  - `slice-goal-loop` — `Goal` table + `/goals`, `/goals/{id}/run`, `/goals/{id}/next`, `/goals/{id}`; `harness/patterns/goal-loop.md`.
  - `slice-generated-tests` — `tests/test_chat.py` covers stub, run_id, runs, goal loop.

### Phase 3 — Deploy Template (shipped)

- **Shipped slices:**
  - `slice-deploy-dockerfile` — `deploy/Dockerfile` multi-stage backend image.
  - `slice-deploy-gcp` — `deploy/gcp-vm-startup.sh`, `deploy/terraform/main.tf`, `deploy/cloudbuild.yaml`, `deploy/README.md`.

### Phase 4 — Capability Plugin (shipped)

- **Shipped slices:**
  - `slice-capability-stub` — `capabilities/README.md` + `capabilities/example.md` describing the one-file-per-capability convention the supervisor can route to.
  - `slice-capability-loader` — `app/capabilities.py` loads `capabilities/*.md` at startup into a `{slug: doc}` route table; exposed via `GET /capabilities`.
- **Goal:** Drop a new `capabilities/<slug>.md` to register a capability the supervisor can route by name.
- **Dependencies:** Phase 2.
