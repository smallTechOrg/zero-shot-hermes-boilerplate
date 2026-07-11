# zero-shot-sdd-harness — working scaffold + boilerplate

This repo is **the scaffold itself**: a runnable multi-agent hackathon starter-kit.
No generator step — the code lives directly in the repo and runs as-is.

## What's in here

- `backend/` — FastAPI + SQLAlchemy + SQLite. Supervisor/worker agent graph, run + goal persistence, Hermes goal loop.
- `frontend/` — React + TypeScript + Vite + Tailwind chat UI.
- `deploy/` — GCP VM path: `Dockerfile`, `gcp-vm-startup.sh`, `terraform/main.tf`, `cloudbuild.yaml`.
- `capabilities/` — one-file-per-capability plugin convention.
- `harness/` — Hermes-native skill/agent/pattern stubs (how to build with this kit).
- `spec/` — product spec (single source of truth).

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

- `GET /health` → `{"status":"ok"}`
- `POST /api/chat` → `{"reply": "...", "run_id": N}`
- `POST /goals` + `POST /goals/{id}/run` → autonomous multi-step Hermes goal loop

## Docker

```bash
docker compose up --build
# backend :8000, web :5173
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

## Cycle time

Target **20–60 minutes** from idea to a runnable, deployable agent.

## Reuse as a boilerplate

Copy `backend/`, `frontend/`, `deploy/`, `capabilities/` into a new repo and rename
`demo-agent` → your project. The harness stubs in `harness/` show how to extend it
with Hermes skills/agents.
