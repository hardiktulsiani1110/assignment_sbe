from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from db.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, password: str, role: str):
        user = User(email=email, password=password, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def delete(self, user: User) -> bool:
        self.db.delete(user)
        self.db.commit()
        return True
