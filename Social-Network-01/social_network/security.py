from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from typing import Annotated

import logging

from passlib.context import CryptContext

import datetime

from jose import jwt, ExpiredSignatureError, JWTError

from social_network.database import database, users_table

from social_network.config import config

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

oauth2_schema = OAuth2PasswordBearer(tokenUrl='user/token')

def get_token_expire_minutes():
    return config.EXPIRE_MINUTES

def create_access_token(email: str) -> str:
    logger.debug("Creating Access Token", extra={"email": email})

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=get_token_expire_minutes(),
    )

    jwt_data = {"sub": email, "exp": expire}

    # print(f"The Secret Key For Encoding JWT Is: {config.SECRET_KEY}")

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

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail="Couldn't Login",
    headers={
        "WWW-Authenticate": "Bearer",
    }
)

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)

    if not user:
        raise credentials_exception 

    #try:
    if not verify_password(password, user.password):
        raise credentials_exception
    # except Exception as e:
    #         logger.error(f"The Error In Verifying Password Is: {e.__str__()}")
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't Login 2")

    return create_access_token(user.email)

# Annotated[str, Depends(oauth2_schema)] --> That Means The Token Type Is String
# And Will Be Populated From oauth2_schema
async def get_current_user(token: Annotated[str, Depends(oauth2_schema)]):
    try:
        payload = jwt.decode(token=token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM])

        email = payload.get('sub', None)

        if email is None:
            raise credentials_exception
        
        user = await get_user_by_email(email=email)

        if user is None:
            raise credentials_exception
        
        return user
    
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token Has Been Expired",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from e
    except JWTError as e:
        raise credentials_exception from e