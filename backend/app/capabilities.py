"""Capability registry.

Loads every ``capabilities/*.md`` at startup into a ``{slug: doc}`` table so the
supervisor can route a message to a named capability. Drop a new
``capabilities/<slug>.md`` to register a capability — no code change required.

The ``capabilities/`` directory lives at the **repo root** (sibling to ``backend/``)
when running locally, but is copied into the image at ``/app/capabilities`` for
Docker deployments. We search the likely locations so it works in both layouts.
"""

from __future__ import annotations

import re
from pathlib import Path

# Candidate locations for the capabilities/ directory, in priority order.
def _candidate_dirs() -> list[Path]:
    here = Path(__file__).resolve().parent          # backend/app
    return [
        here.parent.parent / "capabilities",        # local: backend/../capabilities
        Path("/app/capabilities"),                  # docker image (backend/Dockerfile)
        Path.cwd() / "capabilities",                # cwd-relative
    ]


_CAPABILITIES: dict[str, str] = {}
_CAPABILITIES_DIR: Path | None = None


def _discover_dir() -> Path | None:
    for d in _candidate_dirs():
        if d.is_dir():
            return d
    return None


def _slug_from_filename(path: Path) -> str:
    return path.stem


def _slug_from_h1(doc: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", doc, re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip().lower()
    # keep alphanumerics, spaces and dashes; collapse to dash-separated slug
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or None


def load_capabilities() -> dict[str, str]:
    """Load (or reload) all capability docs. Returns the slug->doc map."""
    global _CAPABILITIES_DIR
    _CAPABILITIES.clear()
    _CAPABILITIES_DIR = _discover_dir()
    if _CAPABILITIES_DIR:
        for path in sorted(_CAPABILITIES_DIR.glob("*.md")):
            if path.name.upper() == "README.MD":
                continue
            try:
                doc = path.read_text(encoding="utf-8")
            except OSError:
                continue
            slug = _slug_from_h1(doc) or _slug_from_filename(path)
            _CAPABILITIES[slug] = doc
    return dict(_CAPABILITIES)


def get_capabilities() -> dict[str, str]:
    if not _CAPABILITIES:
        load_capabilities()
    return dict(_CAPABILITIES)


def get_capability(slug: str) -> str | None:
    return get_capabilities().get(slug)


def list_capability_slugs() -> list[str]:
    return sorted(get_capabilities().keys())
