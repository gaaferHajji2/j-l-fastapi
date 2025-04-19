from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from typing import Annotated, Literal

import logging

from passlib.context import CryptContext

import datetime

from jose import jwt, ExpiredSignatureError, JWTError

from social_network.database import database, users_table

from social_network.config import config
from social_network.models.user import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/user/token')

def get_access_token_expire_minutes():
    return config.ACCESS_EXPIRE_MINUTES

def get_confirm_token_expire_minutes():
    return config.CONFIRM_EXPIRE_MINUTES

def create_access_token(email: str) -> str:
    logger.debug("Creating Access Token", extra={"email": email})

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=get_access_token_expire_minutes(),
    )

    jwt_data = {"sub": email, "exp": expire, "type": "access"}

    # print(f"The Secret Key For Encoding JWT Is: {config.SECRET_KEY}")

    encoded_jwt = jwt.encode(jwt_data, key=config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt

def create_confirm_token(email: str) -> str:
    logger.debug("Creating Confirm Token", extra={"email": email})

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=get_confirm_token_expire_minutes(),
    )

    jwt_data = {"sub": email, "exp": expire, "type": "confirmation"}

    # print(f"The Secret Key For Encoding JWT Is: {config.SECRET_KEY}")

    encoded_jwt = jwt.encode(jwt_data, key=config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hash: str):
    return pwd_context.verify(password, hash)

async def get_user_by_email(email: str) -> User:

    logger.debug("Fetching Users Data By Email", extra={"email": email})

    query = users_table.select().filter(users_table.c.email == email)

    logging.debug(f"The Query To Get User By Email Is: {query}")

    result = await database.fetch_one(query)

    if result:
        return result

def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = detail,
        headers = {
            "WWW-Authenticate": "Bearer",
        }
    )

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)

    if not user:
        raise create_credentials_exception(detail="User Not Found") 

    #try:
    if not verify_password(password, user.password):
        raise create_credentials_exception(detail="Invalid Email OR Password")
    
    # except Exception as e:
    #         logger.error(f"The Error In Verifying Password Is: {e.__str__()}")
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't Login 2")

    if user.confirmed is None or not user.confirmed:
        raise create_credentials_exception(detail="You Must Confirm URL First")

    return create_access_token(user.email)

def get_subject_for_token_type(token: str, token_type: Literal['access', 'confirmation']) -> str:
    try:
        payload = jwt.decode(token=token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM])
    
    except ExpiredSignatureError as e:
        raise create_credentials_exception(
            detail="Token Has Been Expired",
        ) from e

    except JWTError as e:
        raise create_credentials_exception(detail="Invalid Token") from e
    
    email = payload.get('sub', None)

    if email is None:
        raise create_credentials_exception(detail="Email Not Found")
        
    t1 = payload.get('type')

    # print("*#"*15)
    # print(f"The T1 Value Is: {t1}")
    # print(f"The Token Type Is: {token_type}")
    # print("*#"*15)

    if t1 is None or t1.lower() != token_type.lower():
        raise create_credentials_exception(detail="Invalid Type For Token")
        
    return email
    
# Annotated[str, Depends(oauth2_schema)] --> That Means The Token Type Is String
# And Will Be Populated From oauth2_schema
async def get_current_user(token: Annotated[str, Depends(oauth2_schema)]):
    
    email = get_subject_for_token_type(token=token, token_type='access')
    
    user = await get_user_by_email(email=email)

    if user is None:
        raise create_credentials_exception(detail="Invalid Email OR Password")
    return user