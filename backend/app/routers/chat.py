from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import traceback

from app.config import settings
from app.agent import run_graph
from app.db import SessionLocal
from app.models import Run

router = APIRouter(prefix="/api", tags=["chat"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str
    run_id: int | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    reply, error = await run_graph(messages)
    run_id = None
    db: Session = SessionLocal()
    try:
        run = Run(
            status="error" if error else "succeeded",
            user_message=req.messages[-1].content,
            assistant_message=reply,
            error_message=error,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id
    except Exception:
        db.rollback()
        traceback.print_exc()
    finally:
        db.close()
    return ChatResponse(reply=reply or "Something went wrong.", run_id=run_id)



class RunResponse(BaseModel):
    id: int
    status: str
    user_message: str
    assistant_message: str | None
    error_message: str | None
    created_at: str


class RunListResponse(BaseModel):
    runs: list[RunResponse]


@router.get("/runs", response_model=RunListResponse)
async def list_runs():
    db: Session = SessionLocal()
    try:
        runs = db.query(Run).order_by(Run.id.desc()).limit(50).all()
        return RunListResponse(
            runs=[
                RunResponse(
                    id=run.id,
                    status=run.status,
                    user_message=run.user_message,
                    assistant_message=run.assistant_message,
                    error_message=run.error_message,
                    created_at=run.created_at.isoformat() if run.created_at else "",
                )
                for run in runs
            ]
        )
    finally:
        db.close()


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: int):
    db: Session = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            return RunResponse(
                id=run_id,
                status="not_found",
                user_message="",
                assistant_message=None,
                error_message="Run not found",
                created_at="",
            )
        return RunResponse(
            id=run.id,
            status=run.status,
            user_message=run.user_message,
            assistant_message=run.assistant_message,
            error_message=run.error_message,
            created_at=run.created_at.isoformat() if run.created_at else "",
        )
    finally:
        db.close()
