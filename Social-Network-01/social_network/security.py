from fastapi import HTTPException, status

import logging

from passlib.context import CryptContext

import datetime

from jose import jwt

from social_network.database import database, users_table

from social_network.config import config

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

def get_token_expire_minutes():
    return config.EXPIRE_MINUTES

def create_access_token(email: str) -> str:
    logger.debug("Creating Access Token", extra={"email": email})

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=get_token_expire_minutes(),
    )

    jwt_data = {"sub": email, "exp": expire}

    encoded_jwt = jwt.encode(jwt_data, key=config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hash: str):
    return pwd_context.verify(password, hash)

async def get_user_by_email(email: str):

    logger.debug("Fetching Users Data By Email", extra={"email": email})

    query = users_table.select().filter(users_table.c.email == email)

    logging.debug(f"The Query To Get User By Email Is: {query}")

    result = await database.fetch_one(query)

    if result:
        return result

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't Login 1") 

    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't Login 2") 

    return create_access_token(user.email)