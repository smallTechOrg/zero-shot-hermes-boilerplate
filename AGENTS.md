# Entry Point — `zero-shot-sdd-harness-kit`

This is a spec-driven AI agent **boilerplate**. Read this file first, then read the spec in `spec/` (it is the single source of truth) before touching code.

## What This Repo Is

A runnable, multi-agent hackathon starter-kit. The agent code lives directly in the repo and runs as-is — **there is no generator step** (`bootstrap.py` / `templates/` do not exist). You clone it, install deps, and run it.

- `backend/` — FastAPI + SQLAlchemy + SQLite. Supervisor/worker agent graph, run + goal persistence, Hermes goal loop. **This is the real code** (in `backend/app/`).
- `frontend/` — React + TypeScript + Vite + Tailwind chat UI.
- `deploy/` — GCP VM path: `Dockerfile`, `gcp-vm-startup.sh`, `terraform/main.tf`, `cloudbuild.yaml`.
- `capabilities/` — one-file-per-capability plugin convention (loaded at runtime into a route table).
- `harness/` — Hermes-native skill/agent/pattern **stubs** (methodology for how to extend this kit).
- `spec/` — product spec (single source of truth).
- `.github/workflows/ci.yml` — CI: runs backend tests, evals, frontend build, and builds the deploy image.

> ⚠️ `AGENTS.md` describes **how to build *with* this kit** (the spec-driven workflow in `harness/`). The runnable scaffold is `backend/app/` + `frontend/` — a hand-rolled supervisor/worker graph, **not** the `src/` + LangGraph `transform_text` skeleton some harness docs reference. Those harness docs are the *intended* pattern catalogue; the shipped scaffold is the minimal baseline they describe.

## Run It Locally

```bash
# backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

- `GET /health` → `{"status":"ok","version":"0.1.0"}`
- `POST /api/chat` → `{"reply":"...","run_id":N}` (stub mode unless an LLM key is set)
- `POST /goals` + `POST /goals/{id}/run` → autonomous multi-step goal loop
- `GET /capabilities` → registered capability slugs from `capabilities/*.md`

## Live Mode (real LLM)

Set a key in `.env` (copy from `.env.example`):
- Gemini (default): `LLM_PROVIDER=gemini` + `GEMINI_API_KEY=...` (or `LLM_API_KEY=...`)
- OpenAI-compatible: `LLM_API_KEY=...` + `LLM_BASE_URL=...` + `LLM_MODEL=...`

Without a key the worker returns `[stub] <message>`. The `evals/test_agent.py::test_live_chat` test is skipped unless a key is present.

## Tests & Evals

```bash
cd backend && .venv/bin/activate && python -m pytest tests -v      # unit tests
cd . && backend/.venv/bin/python -m pytest evals -v                 # behaviour evals (live skipped w/o key)
cd frontend && npm run build                                       # tsc + vite
```

## Docker

```bash
docker compose up --build   # backend :8000, web :5173
```

## Deploy to GCP (single VM)

```bash
# manual
gcloud compute instances create demo-agent-vm --machine-type=e2-small \
  --metadata-from-file=startup-script=deploy/gcp-vm-startup.sh
gcloud compute firewall-rules create allow-demo-agent-8000 --allow tcp:8000 --target-tags=demo-agent

# or terraform
cd deploy/terraform && terraform init && terraform apply -var project_id=<YOUR_GCP_PROJECT>
```

See `deploy/README.md` and `harness/patterns/goal-loop.md`.

## Reuse as a Boilerplate

Copy `backend/`, `frontend/`, `deploy/`, `capabilities/` into a new repo and rename `demo-agent` → your project. The harness stubs in `harness/` show how to extend it with Hermes skills/agents.

## Spec Manifest (read in order before writing app code)

```
spec/roadmap.md
spec/architecture.md
spec/api.md
spec/data.md
spec/agent.md
spec/ui.md
harness/rules/ai-agents.md
harness/patterns/phases.md
harness/patterns/project-layout.md
harness/patterns/engineering-practices.md
harness/patterns/test-driven.md
harness/patterns/ui-ux.md
harness/patterns/tech-stack.md
harness/patterns/code.md
harness/patterns/agentic-ai.md
harness/rules/git.md
```

## Skills (entry points)

These are the build-methodology entry points (manual; `disable-model-invocation: true`). Each is invocable as a skill and as a slash command.

| Skill / command | Purpose |
|-----------------|---------|
| `/zero-shot-build [idea]` | Idea → working, verified skeleton (drives the agent-builder). Also adds a capability. |
| `/zero-shot-fix [target]` | Diagnose + fix a bug, error, failing test, or spec/code drift, then verify. |
| `/zero-shot-sync [scope]` | Reconcile spec ↔ code so they match (spec wins), then verify. |

## Key Rules (summary — full rules in harness/rules/ai-agents.md)

- Never write application code before reading the full spec.
- Never skip a phase — complete phase N before starting phase N+1.
- Commit every logical unit of work; never let the working tree stay dirty.
- Each phase is tested by the human before the next phase starts.
- Tight scope, first-time-right — each phase is the smallest user-testable win.
- Tests and evals run against the real LLM/API using keys from `.env` when present; the live eval is gated (skips without a key) so CI never fails on a missing key.
- When in doubt, ask at intake — do not guess requirements.

## Sub-agents (the team)

`/zero-shot-build` delegates a full build to **agent-builder**, which plans and coordinates the rest and owns git/PR. `/zero-shot-fix` and `/zero-shot-sync` call the workers directly. Each agent is one full, self-contained definition at `harness/agents/<name>.md`.

| Agent | Role | Tools |
|-------|------|-------|
| agent-builder | Orchestrator — plans phases, fans out code-generator instances per slice, owns git/PR | read/bash/agent |
| spec-writer | The single design authority — writes the FULL spec and self-reviews it | read/write |
| code-generator | Implements ONE independent slice plus tests | read/write/bash |
| qa-auditor | Independent review + run gates/tests/app + audit spec↔code drift | read-only (bash) |

Pattern: **spec-writer** writes the whole spec; **agent-builder** fans out **code-generator** per slice in parallel; **qa-auditor** independently gates each slice and audits drift.
