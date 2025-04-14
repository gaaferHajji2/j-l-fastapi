from fastapi import APIRouter, HTTPException, status, Form, Depends

from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

import logging

# from passlib.hash import pbkdf2_sha256
 
from social_network.models.user import UserIn

from social_network.security import get_user_by_email, get_password_hash, authenticate_user

from social_network.database import database, users_table

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post('/register', status_code=201)
async def register(user: UserIn):
    t1 = await get_user_by_email(user.email)

    if t1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User Already Exists With That Email"
        )
    
    query = users_table.insert().values(
        email=user.email, 
        password=get_password_hash(user.password)
    )

    logger.debug(f"The Query For Creating User: {query}")

    result = await database.execute(query)

    return {"msg": "User Created Successfully", "id": result}

# @router.post('/token', status_code=200)
# async def login_user(user: UserIn):
#     access_token = await authenticate_user(user.email, user.password)

#     return {"access_token": access_token, "token_type": "bearer"}

@router.post('/token', status_code=200)
async def login_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()], 
    grant_type: Annotated[str, Form()]):
    access_token = await authenticate_user(username, password)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/token', status_code=200)
async def login_user(form_data:  Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = await authenticate_user(form_data.username, form_data.password)

    return {"access_token": access_token, "token_type": "bearer"}