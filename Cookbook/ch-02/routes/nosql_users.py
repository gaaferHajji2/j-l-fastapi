from typing import List

from fastapi import APIRouter, HTTPException

from schemas.user_schema import UserCreate, UserList

from models.user_collection import user_collection

nosql_user_router = APIRouter()

@nosql_user_router.get('/', response_model=List[UserList])
async def get_all_users():
    return [user for user in user_collection.find()]

