from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserSchemaRes, UserSchemaReq
from models.users_model import User
from db import get_async_db_session

user_router = APIRouter()

@user_router.post('/', response_model=UserSchemaRes)
async def create_user(user: UserSchemaReq, db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user