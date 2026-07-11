# Capabilities — demo-agent

Drop one file per discrete capability here. Each file describes exactly one thing
the agent can do. Capabilities are loaded at backend startup from every `*.md` in
this directory (except `README.md`) and exposed via `GET /capabilities`, which
returns the list of registered slugs (derived from each file's `# H1`).

Convention:
- filename = `{capability-slug}.md`
- first H1 = capability name (used as the registered slug, lowercased/dashed)
- sections: Purpose, Inputs, Output, Side-effects

The supervisor (`backend/app/agent.py`) can branch on a capability by name — extend
`_supervisor`/`_worker` to read `app.capabilities.get_capability(slug)` and adjust
the system prompt or routing. `capabilities/example.md` shows the minimal shape.
