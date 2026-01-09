import os
import datetime
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from email_validator import validate_email, EmailNotValidError
from db import get_async_db_session
from util.util import pwd_context
from models.users_model import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/users/token')

async def authenticate_user(session: AsyncSession, email: str, password: str) -> User|None:
    try:
        validate_email(email)
        user = (await session.execute(select(User).filter(User.email == email))).scalar_one_or_none()
        if not user:
            # print("No User Found")
            return None
        if not pwd_context.verify(password, user.password):
            # print("Wrong password")
            return None
        return user
    except EmailNotValidError as e:
        # print(f"error in email: {e}")
        return None

async def create_jwt_token(data: dict) -> str:
    payload = data.copy()
    expire_time = datetime.datetime.now(datetime.timezone.utc) \
        + datetime.timedelta(
            minutes=float(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    )
    payload.update({'exp': expire_time})
    token = jwt.encode(payload, os.environ.get('SECRET_KEY', ''), algorithm=os.environ.get('ALGORITHM', ''))
    return token

async def get_user_from_token(token: Annotated[str, Depends(oauth2_schema)], session: Annotated[AsyncSession, Depends(get_async_db_session)]) -> User | None:
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', ''), algorithms=os.environ.get('ALGORITHM', ''))
        email: str | None = payload.get("sub")
        if email is None:
            return None
        user = (await session.execute(select(User).filter(User.email == email))).scalar_one_or_none()
        # print(f"User is: {user}")
        return user
    except JWTError:
        print(f"Check Your JWT {token}")
        return None