# Zero Shot SDD Harness — Hermes Port

A **Hermes-native** port of the spec-driven-development (SDD) harness for building
agents spec-first. The original is Claude Code native:
`/Users/sai/Workspace/Lab/zero-shot-sdd-harness` (also published at
`smallTechOrg/zero-shot-sdd-harness`).

This repository re-expresses that harness for **Hermes Agent** — same six convictions,
same spec-first discipline, same human-gated phased build — but using Hermes-native
conventions instead of `.claude/`:

| Claude Code original | Hermes port |
|---|---|
| `CLAUDE.md` entry point | `AGENTS.md` (root) + `.hermes.md` |
| `.claude/skills/<name>/SKILL.md` | `~/.hermes/skills/` style SKILL.md under `harness/skills/` |
| `.claude/agents/*.md` (sub-agents) | `harness/agents/*.md` (run via `delegate_task`) |
| `.claude/commands/*.md` slash commands | Hermes slash-command-style entry points in `harness/skills/` |
| `ToolSearch` + `AskUserQuestion` | Hermes `clarify` tool + `delegate_task` |

## The Spirit (unchanged)

1. **Spec is the source of truth.** Written before code; when spec and code disagree,
   the spec wins (`/zero-shot-sync` equivalent).
2. **Built for two audiences at once.** A non-coder drives it with a sentence; a senior
   engineer inherits a reviewable stack.
3. **Lean harness, not a framework.** `harness/` is engineering mindfulness — kept small.
4. **Smallest first-time-right win, phase by phase.** Each phase ships the smallest
   testable increment and must work the first time.
5. **A human gates every phase.** Autonomous within a phase; you test before the next starts.
6. **Real LLM/API or it doesn't count.** Gates run against the real model with keys
   from `.env` — never a stubbed pass.

## Status

- `main` — this minimal scaffold only.
- **`v0.1`** (PR) — the full harness port: `AGENTS.md`, `harness/rules/`,
  `harness/patterns/`, `harness/agents/` (Hermes-adapted sub-agent roles), and
  `harness/skills/` (the `zero-shot-build` / `zero-shot-fix` / `zero-shot-sync`
  workflows expressed for Hermes). See the open PR titled **`v0.1`**.

## Repo Layout (target after v0.1)

```
AGENTS.md                 ← Hermes entry point (port of CLAUDE.md)
.hermes.md                ← Hermes context file (hierarchical rules)
harness/
  rules/                  ← ai-agents, git, secret-hygiene (Hermes-adapted)
  patterns/               ← spec-driven, phases, project-layout, tech-stack,
                             code, test-driven, ui-ux, agentic-ai, engineering-practices
  agents/                 ← Hermes sub-agent role defs (port of .claude/agents)
  skills/                 ← zero-shot-build / zero-shot-fix / zero-shot-sync (Hermes form)
spec/                     ← your spec: roadmap, architecture, capabilities/, data, api, ui, agent
src/                     ← baseline agent (ported runtime)
frontend/                ← UI
tests/
.gitignore
.env.example
```

## License

MIT
