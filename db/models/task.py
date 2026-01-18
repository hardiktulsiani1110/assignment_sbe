import uuid

from sqlalchemy import (
    UUID,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    func,
)
from sqlalchemy.orm import relationship

from db.database import Base

# creating a user task junction table
task_collaborators = Table(
    "task_collaborators",
    Base.metadata,
    Column(
        "task_id", UUID, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="icebox")
    priority = Column(String, nullable=False, default="low")
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    parent_task_id = Column(
        UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_tasks")
    parent_task = relationship(
        "Task",
        foreign_keys=[parent_task_id],
        remote_side=[id],
        back_populates="subtasks",
    )
    subtasks = relationship(
        "Task", foreign_keys=[parent_task_id], back_populates="parent_task"
    )
    collaborators = relationship(
        "User", secondary=task_collaborators, back_populates="collaborated_tasks"
    )

    __table_args__ = (
        CheckConstraint(
            "status in ('icebox', 'in_progress', 'completed', 'overdue', 'deleted')",
            name="ck_status",
        ),
        CheckConstraint("priority in ('low', 'medium', 'high')", name="ck_priority"),
    )
