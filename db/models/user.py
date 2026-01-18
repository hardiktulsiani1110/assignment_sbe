import uuid

from sqlalchemy import UUID, CheckConstraint, Column, String
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="member", nullable=False)

    # relationships
    owned_tasks = relationship(
        "Task", foreign_keys="Task.owner_id", back_populates="owner"
    )
    collaborated_tasks = relationship(
        "Task", secondary="task_collaborators", back_populates="collaborators"
    )

    __table_args__ = (CheckConstraint("role IN ('admin','member','manager')"),)
