"""
# add user
# delete user
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.http.users import AddUserRequest
from src.infrastructure.db.async_db import get_db_session
from src.infrastructure.db.repository.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.application.usecases.user_usecase import UserUseCase
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/add",
             status_code=status.HTTP_201_CREATED,
             description="add user.",
             )
async def add_user(request_model: AddUserRequest,
                   req: Request,
                   db_session: AsyncSession = Depends(get_db_session)
                   ):
    user_db_repo = SQLAlchemyUserRepository(db_session)
    user_usecase = UserUseCase(password_hasher=req.app.state.password_hasher,
                               user_db_repo=user_db_repo
                               )
    try:
        async with db_session.begin():
            await user_usecase.add_user(request_model.user_id, request_model.user_pw)
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

