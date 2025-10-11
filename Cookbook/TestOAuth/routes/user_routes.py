from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserSchemaRes, UserSchemaReq
from models.users_model import User
from db import get_async_db_session
from util.util import pwd_context

user_router = APIRouter()

@user_router.post('/', response_model=UserSchemaRes)
async def create_user(user: UserSchemaReq, db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    print(f"The user Password is: {user.password}")
    user.password = pwd_context.hash(user.password)

    t2 = await db.execute(select(User).filter(User.email == user.email))
    t2 = t2.scalar_one_or_none()

    if t2 is not None:
        raise HTTPException(status_code=404, detail={ "msg" : "Email Exists change it" })

    t1 = User(**user.model_dump())
    db.add(t1)
    await db.commit()
    await db.refresh(t1)

    return t1