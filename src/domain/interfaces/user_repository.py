from abc import ABC, abstractmethod
from src.domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def add_user(self, user_dom: User):
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_user_by_id(self, user_id: str):
        raise NotImplementedError
