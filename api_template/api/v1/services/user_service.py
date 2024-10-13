import logging
from typing import List, Optional, Tuple

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from api_template.api.v1.auth.auth import get_password_hash
from api_template.api.v1.repositories.user_repository import UserRepository
from api_template.api.v1.schemas.user_schemas import UserCreate, UserUpdate
from api_template.db.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db):
        self.repository = UserRepository(db)

    async def create_user(self, user: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            logger.warning(f"Attempted to create user with existing email: {user.email}")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="User with this email already exists"
            )

        hashed_password = get_password_hash(user.password)
        user_data = UserCreate(**user.dict(), hashed_password=hashed_password)
        new_user = await self.repository.create(user_data)
        logger.info(f"New user created: {new_user.id}")
        return new_user

    async def get_users(self, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        users = await self.repository.get_all(skip, limit)
        total = users.count("*")
        return users, total

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        existing_user = await self.repository.get(user_id)
        if not existing_user:
            logger.warning(f"Attempted to update non-existent user: {user_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        updated_user = await self.repository.update(user_id, user_update)
        logger.info(f"User updated: {user_id}")
        return updated_user

    async def delete_user(self, user_id: int) -> bool:
        existing_user = await self.repository.get(user_id)
        if not existing_user:
            logger.warning(f"Attempted to delete non-existent user: {user_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        result = await self.repository.delete(user_id)
        if result:
            logger.info(f"User deleted: {user_id}")
        return result

    async def notify_user(self, user_id: int, message_type: str, content: str):
        # Implement notification logic here
        logger.info(f"Notification sent to user {user_id}: {message_type}")
        pass
