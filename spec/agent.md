# Agent — `scaffold-agent`

> Phase 1 shipped the agent stub. Phase 2 replaces `/api/chat` with a compact multi-agent supervisor graph plus run persistence.

---



**Chosen:** Multi-agent supervisor by default, with ReAct worker nodes, plus a lightweight goal loop for autonomous multi-step runs.

## Goal Loop

The generated harness supports optional goal-based looping so Hermes or similar automation can drive the agent through multiple steps without manual intervention.

### State shape

```python
class GoalState(TypedDict):
    goal_id: int
    run_id: int
    goal_text: str
    status: str
    step_index: int
    steps: list[dict]
    last_reply: str | None
    last_error: str | None
```

Loop rules:
- `pending` → `running` → `succeeded` / `failed`
- A step may finish with `intermediate` to continue the loop
- `next_step` advances once per successful iteration
- Hard stop on `failed` or terminal `succeeded`

### Endpoints

- `POST /goals` create a goal with initial step list
- `POST /goals/{goal_id}/next` advance one step
- `POST /goals/{goal_id}/run` run loop until termination
- `GET /goals/{goal_id}` current goal state

### Persistence

Goals and step receipts are stored in `app/models.py` and materialized by `app/db.py` on startup.

## Supervisor

The backend emits a supervisor graph in `app/agent.py`:
- START -> supervisor -> worker -> END
- worker may return reply, error, or a follow-up step

| Node | Provider | Model ID | Rationale |
|-------|----------|----------|-----------|
| agent_node | Optional | gpt-4o-mini or claude-haiku-3-5-20240307 | Live responses when `LLM_API_KEY` is set; otherwise degraded to stub path. |

**Fallback behaviour:**
- Missing/invalid key → stub path. No retries, no delays.
- Network failure → 500 with message "LLM call failed"; logged with traceback.

**Prompt strategy:**
- Phase 1: static prompt template `You are a helpful assistant.` with user message appended.
- Phase 2: replace with system prompt from `prompts/transform.md` placeholder.

## Tools & Tool Calling

| Tool name | Description | Inputs | Output | Side-effects |
|-----------|-------------|--------|--------|--------------|
| echo | Returns stub reply echoing user input. | messages | string | None |
| llm_call | Calls configured OpenAI-compatible endpoint. | messages, model | string | Network call |

**Tool selection strategy:**
- Phase 1: if `LLM_API_KEY` is set, always use `llm_call`.

**Tool failure handling:**
- On failure: raise 500 with "LLM call failed".

## Agent State

```python
class AgentState(TypedDict):
    run_id: int                # set at entry
    messages: list             # full conversation so far
    reply: str | None          # final assistant message
    error: str | None          # fatal error, if any
```

## Nodes / Steps

### `agent_node`

**Reads from state:** `messages`
**Writes to state:** `reply`, `error`
**LLM call:** yes, if configured; uses a small static prompt.
**External calls:** OpenAI-compatible or Anthropic-compatible client.

**Behaviour:**
- Build prompt from the last user message.
- If a live provider is configured, return the model output.
- Otherwise return a string prefixed with `[stub]` plus the user message.

### `handle_error`

**Reads from state:** `error`
**Writes to state:** sets `reply` to an error string.
**Behaviour:** terminate graph with "Something went wrong."

## Graph / Flow Topology

```text
START -> supervisor -> worker -> END
                   |-> reply -> END
                   |-> error -> handle_error -> END
```

The backend now emits a supervisor graph in `app/graph.py`, a worker node in `app/nodes/*`, and a single entrypoint in `app/agent.py`. `/api/chat` invokes the graph and persists a `Run` record on completion or failure.

## Memory & Context

- Within a run: full messages list in memory.
- Across runs: none in Phase 1 (database receipt is optional).

## Error Handling & Recovery

- Node-level: try/except around LLM call; sets `error`.
- Graph-level: `handle_error` node sets assistant-facing message and returns.

## Observability

- Structured log on every `/api/chat` request: `run_id`, `status`, `latency_ms`.
- Errors logged with full traceback.

## Concurrency Model

- One FastAPI worker per process; SQLite allows one writer at a time, which is sufficient for local dev.
- Threaded `ProcessPoolExecutor` may be used for blocking LLM calls in production.
