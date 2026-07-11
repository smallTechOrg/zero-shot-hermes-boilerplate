# Data Model — `scaffold-agent`

---

## Storage Technology

SQLite (dev) via SQLAlchemy 2.0 core. Tables are created with `Base.metadata.create_all` on import in dev. Production can use Alembic (`alembic upgrade head`). Swap to Postgres by changing `DATABASE_URL` — the ORM models need no code change.

## Entities

### Entity: `Run`

Represents a single agent invocation. Used for observability in dev.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | yes | Primary key |
| created_at | DateTime | yes | Run start time |
| status | String(32) | yes | `succeeded` / `error` |
| agent_id | String(128) | no | Optional agent/session tag |
| user_message | Text | yes | Last user message (what the user sent). |
| assistant_message | Text | no | Generated reply, if any. |
| error_message | Text | no | Reason for failure, if any. |
| trace | Text | no | Optional trace (unused in base scaffold). |

### Entity: `Goal`

Represents an autonomous multi-step run driven by the goal loop.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | yes | Primary key |
| created_at | DateTime | yes | Creation time |
| goal_text | Text | yes | Human-readable goal description |
| status | String(32) | yes | `pending` / `running` / `succeeded` / `failed` |
| steps | Text (JSON) | yes | JSON list of `{"description": "..."}` steps |
| step_index | Integer | yes | Number of steps completed |
| last_reply | Text | no | Reply from the most recent step |
| last_error | Text | no | Error from the most recent step, if any |
| run_id | Integer | no | Optional link to a `Run` |

## Data Lifecycle

- `Run` created on `POST /api/chat`; updated with the reply/error.
- `Goal` created on `POST /goals`; `step_index`/`status` updated as steps execute.
- No deletion strategy in the base scaffold; the `data/` SQLite file can be deleted to reset.

## Sensitive Data

- `.env` is git-ignored. No secrets are committed. Chat content is stored locally only.
