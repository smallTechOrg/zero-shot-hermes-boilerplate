from fastapi import APIRouter

from app import capabilities as _capabilities

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("")
async def list_capabilities():
    """Registered capabilities loaded from capabilities/*.md at startup."""
    return {"capabilities": _capabilities.list_capability_slugs()}
