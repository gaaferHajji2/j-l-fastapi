import logging

from passlib.context import CryptContext

import datetime

from jose import jwt

from social_network.database import database, users_table

from social_network.config import config

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(email: str) -> str:
    logger.debug("Creating Access Token", extra={"email": email})

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=30
    )

    jwt_data = {"sub": email, "exp": expire}

    encoded_jwt = jwt.encode(jwt_data, config.SECRET_KEY, algorithm=config.ALGORITHM)

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