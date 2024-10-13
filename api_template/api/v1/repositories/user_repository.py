from sqlalchemy.orm import Session

from api_template.api.v1.repositories.base_repository import BaseRepository
from api_template.api.v1.schemas.user_schemas import UserCreate, UserUpdate
from api_template.db.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    async def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    async def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    async def create(self, user: UserCreate) -> User:
        db_user = User(
            email=user.email,
            hashed_password=user.password,  # In reality, hash the password
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def update(self, user_id: int, user_update: UserUpdate) -> User | None:
        db_user = self.get_by_id(user_id)
        if db_user:
            update_data = user_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    async def delete(self, user_id: int) -> bool:
        db_user = self.get_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
