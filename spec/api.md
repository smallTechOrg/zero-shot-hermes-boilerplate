# API — `scaffold-agent`

> Run commands are exact. Stubs fail gracefully; live path passes when a key is in `.env`.

---

## API Style

REST (FastAPI). CORS is open (`*`) for local dev. Auth is disabled in the scaffold; add it before production.

## Endpoints

### `GET /health`

**Purpose:** Liveness + DB connectivity check.

**Response (200 OK):**
```json
{ "status": "ok", "version": "0.1.0" }
```

**Error cases:**
| Status | Condition |
|--------|-----------|
| 200 with `{"status":"error"}` | DB connection failed (still HTTP 200, but payload signals failure). |

---

### `POST /api/chat`

**Purpose:** Primary agent entry point. Routes the message through the supervisor/worker graph, persists a `Run`, returns the reply.

**Request:**
```json
{
  "messages": [
    { "role": "user", "content": "Hello" }
  ]
}
```

**Response (200 OK):**
```json
{ "reply": "[stub] Hello", "run_id": 1 }
```

When `LLM_API_KEY` (or the provider key) is present and `LLM_BASE_URL` is set, the worker calls the OpenAI-compatible `/v1/chat/completions` endpoint and returns the model's reply (no `[stub]` prefix).

**Error cases:**
| Status | Condition |
|--------|-----------|
| 422 | Pydantic validation failure (`messages` missing/empty). |
| 200 (run persisted with `status=error`) | Worker raised; `reply` is an error message. |

---

### `GET /api/runs`

**Purpose:** List the most recent persisted run receipts (observability/debugging).

**Response (200 OK):**
```json
{
  "runs": [
    {
      "id": 1,
      "status": "succeeded",
      "user_message": "Hello",
      "assistant_message": "[stub] Hello",
      "error_message": null,
      "created_at": "2026-07-11T19:10:00"
    }
  ]
}
```

### `GET /api/runs/{run_id}`

**Purpose:** Inspect one run receipt. Returns `status:"not_found"` (HTTP 200) if missing.

---

## Goal Loop Endpoints

### `POST /goals`

**Purpose:** Create a goal with an ordered step list.

**Request:**
```json
{
  "goal_text": "Deploy demo-agent to GCP",
  "steps": [
    {"description": "Build backend Docker image"},
    {"description": "Push to GCR"},
    {"description": "Deploy on GCE"}
  ]
}
```

**Response (200 OK):**
```json
{ "goal_id": 1, "status": "pending", "step_index": 0 }
```

### `POST /goals/{goal_id}/next`

**Purpose:** Execute exactly one pending step and return the result.

**Response (200 OK):**
```json
{
  "goal_id": 1,
  "status": "running",
  "step_index": 1,
  "step": {"description": "Build backend Docker image"},
  "reply": "...",
  "error": null
}
```

### `POST /goals/{goal_id}/run`

**Purpose:** Execute remaining steps in a loop until terminal state (`succeeded` or `failed`).

**Response (200 OK):**
```json
{ "goal_id": 1, "status": "succeeded", "step_index": 3, "reply": "..." }
```

Loop rules:
- `pending` → `running` → `succeeded` / `failed`.
- Each step runs the supervisor/worker graph on the step's description.
- On a worker error the goal status becomes `failed` and the loop stops.
- When all steps are done the status becomes `succeeded`.

### `GET /goals/{goal_id}`

**Purpose:** Inspect current goal state (status, `step_index`, last reply/error).

---

## Capabilities

### `GET /capabilities`

**Purpose:** List registered capabilities loaded from `capabilities/*.md` at startup.

**Response (200 OK):**
```json
{ "capabilities": ["example-capability"] }
```
