import pytest

from src.application.usecases.user_usecase import UserUseCase


class FakeRepo:
    async def add_user(self, user): pass
    async def get_user_by_id(self, user_id): pass


class FakeHasher:
    async def hash_password(self, pw):
        return "hashed"


@pytest.mark.asyncio
async def test_add_user_calls_repo():
    repo = FakeRepo()
    hasher = FakeHasher()
    uc = UserUseCase(hasher, repo)
    await uc.add_user("u1", "pw")