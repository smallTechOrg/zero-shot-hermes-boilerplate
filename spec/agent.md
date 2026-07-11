# Agent — `scaffold-agent`

> The agent graph shipped in `app/agent.py`. This describes the real implementation, not a planned one.

---

## Chosen Graph

A **hand-rolled supervisor/worker** graph (no LangGraph dependency). Lightweight goal loop for autonomous multi-step runs.

## Supervisor

`app/agent.py` defines `run_graph(messages)` which runs three nodes in sequence:

```
START -> supervisor -> worker -> END
                     |-> error -> handle_error -> END
```

| Node | Role |
|------|------|
| `_supervisor` | Sets default route/decision; records the last user message. |
| `_worker` | If a key is configured, POSTs to the OpenAI-compatible `/v1/chat/completions` endpoint and stores the reply. Otherwise returns `[stub] <last user message>`. On exception, sets `state["error"]`. |
| `_handle_error` | Terminates with a user-facing error message. |

**Provider / model config** (from `app/config.py`):
- `LLM_PROVIDER` — `gemini` (default) | `openai`.
- `LLM_API_KEY` or `GEMINI_API_KEY` — enables live mode.
- `LLM_BASE_URL` — OpenAI-compatible base URL (default Gemini OpenAI-compat endpoint).
- `LLM_MODEL` — model id (default `gemini-1.5-flash`).

**Fallback behaviour:**
- Missing/invalid key → `[stub]` path. No retries, no delays.
- Network/API failure → `state["error"]` set; `handle_error` returns a message; the `Run` is persisted with `status=error`.

**Prompt strategy:**
- Phase 1: static system prompt `"You are a helpful assistant."` with the last user message appended. Replace in `app/agent.py` (`_worker`) to customize.

## Tools & Tool Calling

| Tool name | Description | Inputs | Output | Side-effects |
|-----------|-------------|--------|--------|--------------|
| echo (stub) | Returns `[stub]` reply echoing user input. | messages | string | None |
| llm_call | Calls the configured OpenAI-compatible endpoint. | messages, model | string | Network call |

**Tool selection:** if a live key is configured, always use `llm_call`; otherwise the stub.

## Agent State

```python
class AgentState(dict):
    run_id: int | None
    messages: list[dict[str, str]]
    reply: str | None
    error: str | None
    route: str          # default "worker"
    decision: str       # default "answer"
    reason: str
    last_user_message: str
```

## Goal Loop

The goal loop drives `_execute_step` per step, calling `run_graph` on each step's `description`. State machine: `pending` → `running` → `succeeded` / `failed`. Endpoints: `POST /goals`, `POST /goals/{id}/next`, `POST /goals/{id}/run`, `GET /goals/{id}`. Goals and steps are stored in `app/models.py` (`Goal`) and materialized via `app/db.py`.

## Capabilities

`app/capabilities.py` loads every `capabilities/*.md` at startup into a `{slug: doc}` table, exposed via `GET /capabilities`. The supervisor can route a message to a named capability (extend `_supervisor`/`_worker` to branch on `capabilities/` content). See `capabilities/README.md` for the one-file-per-capability convention.

## Memory & Context

- Within a run: full `messages` list in memory.
- Across runs: none in the base scaffold (database receipt is for observability only).

## Error Handling & Recovery

- Node-level: `try/except` around the LLM call; sets `error`.
- Graph-level: `handle_error` sets the assistant-facing message and returns.

## Observability

- Every `/api/chat` persists a `Run` row (`status`, `user_message`, `assistant_message`, `error_message`).
- `GET /api/runs` and `GET /api/runs/{id}` for inspection.
- Errors logged to stderr with traceback in the chat router.

## Concurrency Model

- One FastAPI worker per process; SQLite allows one writer at a time, which is sufficient for local dev. For production, point `DATABASE_URL` at Postgres.
