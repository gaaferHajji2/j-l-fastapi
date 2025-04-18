from fastapi import APIRouter, HTTPException, status, Request, Depends

from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

import logging

# from passlib.hash import pbkdf2_sha256

from social_network.models.user import UserIn

from social_network.security import (
    get_user_by_email,
    get_password_hash,
    authenticate_user,
    get_subject_for_token_type,
    create_confirm_token,
)

from social_network.database import database, users_table

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn, request: Request):
    t1 = await get_user_by_email(user.email)

    if t1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Already Exists With That Email",
        )

    query = users_table.insert().values(
        email=user.email, password=get_password_hash(user.password),
        confirmed=False,
    )

    logger.debug(f"The Query For Creating User: {query}")

    result = await database.execute(query)

    return {
        "msg": "User Created Successfully", 
        "id": result,
        "confirmation_url": request.url_for(
            "confirm_user_email",
            token=create_confirm_token(user.email)
        )
    }


# @router.post('/token', status_code=200)
# async def login_user(user: UserIn):
#     access_token = await authenticate_user(user.email, user.password)

#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post('/token', status_code=200)
# async def login_user(
#     username: Annotated[str, Form()],
#     password: Annotated[str, Form()],
#     grant_type: Annotated[str, Form()]):
#     access_token = await authenticate_user(username, password)

#     return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", status_code=200)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = await authenticate_user(form_data.username, form_data.password)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_user_email(token: str):
    email = get_subject_for_token_type(token=token, token_type='confirmation')

    query = users_table.update().where(users_table.c.email == email).values(confirmed=True)

    logger.debug(f"The Query For User Confirmation Is: {query}")

    await database.execute(query)

    return { "detail": "User Confirmed" }