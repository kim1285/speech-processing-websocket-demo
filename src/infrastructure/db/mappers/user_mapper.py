"""
class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    hashed_pw = Column(String)

    class User:
    def __init__(self, user_id, hashed_pw):
        self.user_id = user_id
        self.hashed_pw = hashed_pw

"""
from src.infrastructure.db.models.user import UserModel
from src.domain.models.user import User


def to_orm(user_dom: User) -> UserModel:
    return UserModel(user_id=user_dom.user_id, hashed_pw=user_dom.hashed_pw)


def to_dom(user_orm: UserModel) -> User:
    return User(user_id=user_orm.user_id, hashed_pw=user_orm.hashed_pw)
