from src.infrastructure.security.pw_hasher import PasswordHasher
from src.domain.models.user import User
from src.domain.interfaces.user_repository import UserRepository


class UserUseCase:
    def __init__(self,
                 password_hasher: PasswordHasher,
                 user_db_repo: UserRepository
                 ):
        self.password_hasher = password_hasher
        self.user_db_repo = user_db_repo

    async def add_user(self, user_id: str, user_plain_pw: str) -> None:
        # check if user exists
        user_dom = await self.user_db_repo.get_user_by_id(user_id)
        if user_dom:
            raise Exception("User already exists.")

        # hash pw
        hashed_pw = self.password_hasher.hash_password(user_plain_pw)

        # create user dom obj with user_id, hashed pw
        user_dom_obj = User(user_id=user_id, hashed_pw=hashed_pw)

        # persist user orm obj to db using repo
        await self.user_db_repo.add_user(user_dom_obj)




