"""
1. get pw
2. hash password
3. return hashed password
4. verify hashed password stored on db with plain password
"""
from passlib.context import CryptContext


class PasswordHasher:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, plain_pw: str) -> str:
        return self.pwd_context.hash(plain_pw)

    def verify_password(self, plain_pw: str, hashed_pw: str) -> bool:
        return self.pwd_context.verify(plain_pw, hashed_pw)

