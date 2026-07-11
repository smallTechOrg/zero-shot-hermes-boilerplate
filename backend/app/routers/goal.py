from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import json

from app.db import SessionLocal
from app.models import Goal
from app.agent import run_graph

router = APIRouter(prefix="/goals", tags=["goals"])


class Step(BaseModel):
    description: str


class GoalRequest(BaseModel):
    goal_text: str
    steps: list[Step] = Field(default_factory=list)


class GoalResponse(BaseModel):
    goal_id: int
    status: str
    step_index: int = 0
    step: dict | None = None
    reply: str | None = None
    error: str | None = None


async def _execute_step(goal: Goal, db: Session) -> None:
    steps = json.loads(goal.steps)
    if goal.step_index >= len(steps):
        return
    step = steps[goal.step_index]
    reply, error = await run_graph([{"role": "user", "content": step["description"]}])
    goal.step_index += 1
    goal.last_reply = reply
    goal.last_error = error
    if error:
        goal.status = "failed"
    elif goal.step_index >= len(steps):
        goal.status = "succeeded"
    else:
        goal.status = "running"
    db.add(goal)
    db.commit()


@router.post("", response_model=GoalResponse)
async def create_goal(req: GoalRequest):
    db: Session = SessionLocal()
    try:
        goal = Goal(
            goal_text=req.goal_text,
            steps=json.dumps([s.model_dump() for s in req.steps]),
            status="pending",
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return GoalResponse(goal_id=goal.id, status=goal.status)
    finally:
        db.close()


@router.post("/{goal_id}/next", response_model=GoalResponse)
async def next_step(goal_id: int):
    db: Session = SessionLocal()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return GoalResponse(goal_id=goal_id, status="not_found")
        steps = json.loads(goal.steps)
        if goal.step_index >= len(steps):
            goal.status = "succeeded"
            db.commit()
            return GoalResponse(goal_id=goal_id, status="succeeded")
        await _execute_step(goal, db)
        step = steps[goal.step_index - 1] if goal.step_index > 0 else None
        return GoalResponse(
            goal_id=goal_id,
            status=goal.status,
            step_index=goal.step_index,
            step=step,
            reply=goal.last_reply,
            error=goal.last_error,
        )
    finally:
        db.close()


@router.post("/{goal_id}/run", response_model=GoalResponse)
async def run_goal(goal_id: int):
    db: Session = SessionLocal()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return GoalResponse(goal_id=goal_id, status="not_found")
        goal.status = "running"
        db.commit()
        while goal.status == "running":
            await _execute_step(goal, db)
        return GoalResponse(
            goal_id=goal_id,
            status=goal.status,
            step_index=goal.step_index,
            reply=goal.last_reply,
        )
    finally:
        db.close()


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: int):
    db: Session = SessionLocal()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return GoalResponse(goal_id=goal_id, status="not_found")
        steps = json.loads(goal.steps)
        step = steps[goal.step_index - 1] if 0 < goal.step_index <= len(steps) else None
        return GoalResponse(
            goal_id=goal_id,
            status=goal.status,
            step_index=goal.step_index,
            step=step,
            reply=goal.last_reply,
            error=goal.last_error,
        )
    finally:
        db.close()
