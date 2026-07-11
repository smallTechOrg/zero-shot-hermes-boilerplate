# Hermes Goal Loop

The generated backend ships an opinionated goal loop so Hermes (or any automation)
can drive the agent through multiple steps without manual orchestration.

## Endpoints
- POST /goals -> create goal with ordered steps
- POST /goals/{id}/next -> advance exactly one step
- POST /goals/{id}/run -> loop until terminal state
- GET /goals/{id} -> current state

## Loop contract
- status: pending -> running -> succeeded | failed
- worker returns intermediate -> loop continues
- worker returns succeeded/failed -> loop stops
- no remaining steps after intermediate -> succeeded

## How Hermes uses it
1. POST /goals with the full step plan.
2. POST /goals/{id}/run to let the supervisor execute every step autonomously.
3. Poll GET /goals/{id} for terminal status and last_reply.

This keeps Hermes from hand-holding each step while preserving a verifiable
receipt per goal in the goals table.
