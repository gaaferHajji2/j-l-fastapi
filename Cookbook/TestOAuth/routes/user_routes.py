from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserSchemaRes, UserSchemaReq
from models.users_model import User
from db import get_async_db_session
from util.util import pwd_context
from security import authenticate_user, create_jwt_token, oauth2_schema, get_user_from_token

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

@user_router.post('/token')
async def get_user_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[AsyncSession, Depends(get_async_db_session)] ):
    user = await authenticate_user(session, form_data.username, form_data.password)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = await create_jwt_token({ "email" : user.email, "type": "access" })

    return {
        "token": token,
        "type": "bearer",
    }

@user_router.get('/me')
async def get_user_profile(token: Annotated[str, Depends(oauth2_schema)], session: Annotated[AsyncSession, Depends(get_async_db_session)]):
    # user = await get_user_from_token(token, session)
    user = await get_user_from_token(token, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user.to_json()