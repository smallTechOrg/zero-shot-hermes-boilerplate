from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(32), nullable=False, default="succeeded")
    agent_id = Column(String(128), nullable=True)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    trace = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    goal_text = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    steps = Column(Text, nullable=False, default="[]")  # JSON list of {description}
    step_index = Column(Integer, nullable=False, default=0)
    last_reply = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)
    run_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
