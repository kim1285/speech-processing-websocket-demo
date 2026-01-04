from src.infrastructure.db.async_db import Base
from sqlalchemy import Column, String


class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    hashed_pw = Column(String)
