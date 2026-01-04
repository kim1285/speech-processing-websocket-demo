from pydantic import BaseModel


class AddUserRequest(BaseModel):
    user_id: str
    user_pw: str
