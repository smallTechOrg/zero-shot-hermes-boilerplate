from __future__ import annotations

from typing import Any

from app.config import settings


class AgentState(dict):
    run_id: int | None
    messages: list[dict[str, str]]
    reply: str | None
    error: str | None


async def _supervisor(state: AgentState) -> AgentState:
    last = state["messages"][-1]["content"] if state["messages"] else ""
    state.setdefault("route", "worker")
    state.setdefault("decision", "answer")
    state.setdefault("reason", "default-worker")
    state["last_user_message"] = last
    return state


async def _worker(state: AgentState) -> AgentState:
    last = state.get("last_user_message", "")
    api_key = settings.resolved_api_key
    if api_key:
        try:
            import httpx

            base_url = settings.LLM_BASE_URL
            model = settings.LLM_MODEL
            # Gemini's OpenAI-compatible endpoint is `<base>/chat/completions`
            # (base already ends in /openai). Standard OpenAI is `<base>/v1/chat/completions`.
            if settings.LLM_PROVIDER == "gemini":
                endpoint = f"{base_url.rstrip('/')}/chat/completions"
            else:
                endpoint = f"{base_url.rstrip('/')}/v1/chat/completions"
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": last},
                    ],
                }
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                resp = await client.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                state["reply"] = data["choices"][0]["message"]["content"]
                return state
        except Exception as exc:
            state["error"] = f"llm:{exc}"
            return state

    state["reply"] = f"[stub] {last}"
    return state


async def _handle_error(state: AgentState) -> AgentState:
    state.setdefault("reply", "Something went wrong.")
    if state.get("error"):
        state["reply"] = f"Something went wrong: {state['error']}"
    return state


NODES = {
    "supervisor": _supervisor,
    "worker": _worker,
    "handle_error": _handle_error,
}


async def run_graph(messages: list[dict[str, str]]) -> tuple[str, str | None]:
    state: AgentState = {
        "run_id": None,
        "messages": messages,
        "reply": None,
        "error": None,
        "route": "worker",
        "decision": "answer",
        "reason": "default",
    }

    state = await _supervisor(state)
    if state.get("error"):
        state = await _handle_error(state)
        return state["reply"], state.get("error")

    state = await _worker(state)
    if state.get("error"):
        state = await _handle_error(state)

    return state["reply"], state.get("error")
