"""
from abc import ABC, abstractmethod


class UserRepository(ABC):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    async def add_user(self, user_id: str, hashed_pw: str):
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: str, hashed_pw: str):
        raise NotImplementedError

"""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.interfaces.user_repository import UserRepository
from src.domain.models.user import User
from src.infrastructure.db.mappers.user_mapper import to_orm, to_dom
from src.infrastructure.db.models.user import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user_dom: User):
        user_orm = to_orm(user_dom)
        self.session.add(user_orm)

    async def get_user_by_id(self, user_id: str) -> User | None:
        stmt = select(UserModel).where(UserModel.user_id == user_id)
        user_orm = (await self.session.execute(stmt)).scalar_one_or_none()
        if not user_orm:
            return
        user_dom = to_dom(user_orm)
        return user_dom

    async def delete_user_by_id(self, user_id: str):
        stmt = delete(UserModel).where(UserModel.user_id == user_id)
        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            raise Exception("User not found.")








