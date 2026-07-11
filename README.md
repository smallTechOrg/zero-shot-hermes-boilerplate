# zero-shot-sdd-harness — runnable scaffold + boilerplate

This repo is **the scaffold itself**: a runnable multi-agent hackathon starter-kit.
No generator step — the code lives directly in the repo and runs as-is.

## What's in here

- `backend/` — FastAPI + SQLAlchemy + SQLite. Supervisor/worker agent graph, run + goal persistence, Hermes goal loop, capability registry.
- `frontend/` — React + TypeScript + Vite + Tailwind chat UI.
- `deploy/` — GCP VM path: `Dockerfile`, `gcp-vm-startup.sh`, `terraform/main.tf`, `cloudbuild.yaml`.
- `capabilities/` — one-file-per-capability plugin convention (loaded at runtime).
- `harness/` — Hermes-native skill/agent/pattern stubs (how to build *with* this kit).
- `spec/` — product spec (single source of truth).
- `.github/workflows/ci.yml` — CI: backend tests, evals, frontend build, deploy-image build.

## Run it locally

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
- `POST /api/chat` → `{"reply":"...","run_id":N}`
- `POST /goals` + `POST /goals/{id}/run` → autonomous multi-step Hermes goal loop
- `GET /capabilities` → registered capability slugs from `capabilities/*.md`

## Live mode (real LLM)

Copy `.env.example` to `.env` and set a key:

- **Gemini (default):** `LLM_PROVIDER=gemini` + `GEMINI_API_KEY=...` (or `LLM_API_KEY=...`)
- **OpenAI-compatible:** `LLM_API_KEY=...` + `LLM_BASE_URL=...` + `LLM_MODEL=...`

Without a key the worker returns `[stub] <message>`. The live eval
(`evals/test_agent.py::test_live_chat`) is skipped unless a key is present, so CI
never fails on a missing key.

## Tests & evals

```bash
cd backend && .venv/bin/activate && python -m pytest tests -v      # unit tests
cd . && backend/.venv/bin/python -m pytest evals -v                 # behaviour evals (live skipped w/o key)
cd frontend && npm run build                                       # tsc + vite
```

## Docker

```bash
docker compose up --build
# backend :8000, web :5173
```

`docker-compose.yml` builds `backend/Dockerfile.backend` and
`frontend/Dockerfile.frontend`. The frontend dev server runs on :5173 with
source bind-mounted; deps install on first start.

## Deploy to GCP (single VM)

```bash
# manual
gcloud compute instances create demo-agent-vm --machine-type=e2-small \
  --metadata-from-file=startup-script=deploy/gcp-vm-startup.sh
gcloud compute firewall-rules create allow-demo-agent-8000 --allow tcp:8000 --target-tags=demo-agent

# or terraform
cd deploy/terraform && terraform init && terraform apply -var project_id=<YOUR_GCP_PROJECT>
```

`deploy/cloudbuild.yaml` builds + pushes the backend image to Artifact Registry;
`deploy/gcp-vm-startup.sh` runs it on the VM. See `deploy/README.md` and
`harness/patterns/goal-loop.md`.

## CI

`.github/workflows/ci.yml` runs on pushes to `main`/`feature/v0.1` and on PRs:
backend unit tests, evals (stub), frontend build, and a backend deploy-image build
on `main`. Merge to `main` to trigger the deploy-image build.

## Cycle time

Target **20–60 minutes** from idea to a runnable, deployable agent.

## Reuse as a boilerplate

Copy `backend/`, `frontend/`, `deploy/`, `capabilities/` into a new repo and rename
`demo-agent` → your project. The harness stubs in `harness/` show how to extend it
with Hermes skills/agents.
