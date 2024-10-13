from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.sql import func

from api_template.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    function_name = Column(String, nullable=False)
    agent_id = Column(Integer, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False)
    input_data = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    retry = Column(Boolean, default=True)
    output_data = Column(String)

    __table_args__ = (Index("idx_task_id", task_id),)
