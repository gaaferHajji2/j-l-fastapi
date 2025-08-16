from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_db_session
from models.user import User

users_router = APIRouter()

@users_router.get('/')
async def get_all_users(db : Annotated[AsyncSession, Depends(get_async_db_session) ]):
    
    result = await db.execute(select(User))

    users = result.scalars()
    # users = result.scalars().all() # This is also valid

    return [user.to_json() for user in users]