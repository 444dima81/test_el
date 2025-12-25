# api/memory.py

from fastapi import APIRouter, Request
from app.api.deps import UserIdDep

router = APIRouter()


@router.post("/memory/clear")
async def memory_clear(request: Request, user_id: str = UserIdDep):
    request.app.state.memory.clear(user_id)
    return {"status": "ok", "user_id": user_id}