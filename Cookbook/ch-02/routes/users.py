from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_db_session
from models.user import User

from schemas.user_schema import UserCreate, UserList

users_router = APIRouter()

@users_router.get('/', response_model=List[UserList])
async def get_all_users(db : Annotated[AsyncSession, Depends(get_async_db_session) ]):
    
    result = await db.execute(select(User))

    users = result.scalars()
    # users = result.scalars().all() # This is also valid

    return users


@users_router.post('/', response_model=UserList, status_code=201)
async def create_new_user(db: Annotated[AsyncSession, Depends(get_async_db_session)], user: UserCreate):

    t1 = User(
        email=user.email,
        name=user.name
    )

    db.add(t1)
    await db.commit()
    await db.refresh(t1)

    return t1

@users_router.get('/{id}', response_model=UserList)
async def get_user_by_id(id: int, db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    user = await db.execute(select(User).filter(User.id == id))

    user = user.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "User not found",
            }
        )
    return user

@users_router.put('/{user_id}', response_model=UserList)
async def update_user(user_id: int, user: UserCreate, db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    t1 = await db.execute(select(User).filter(User.id == user_id))

    t1 = t1.scalar_one_or_none()

    if t1 is None:
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "User not found"
            }
        )
    
    print(t1)

    
    t1.name = user.name
    t1.email = user.email

    await db.commit()

    await db.refresh(t1)

    return t1

@users_router.delete('/{user_id}', status_code=204)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    user = await db.execute(select(User).filter(User.id == user_id))

    user = user.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "User not found"
            }
        )

    await db.delete(user)
    await db.commit()

    return { "result": "User deleted" }