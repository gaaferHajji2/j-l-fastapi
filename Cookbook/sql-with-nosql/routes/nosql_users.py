from typing import List

from fastapi import APIRouter, HTTPException

from bson import ObjectId

from schemas.user_schema import UserCreate, NoSQLUserList

from models.user_collection import user_collection

nosql_user_router = APIRouter()


@nosql_user_router.get("/", response_model=List[NoSQLUserList])
async def get_all_users():
    return [
        NoSQLUserList(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
        )
        for user in user_collection.find()
    ]


@nosql_user_router.post("/", response_model=NoSQLUserList)
async def create_user(user: UserCreate):
    t1 = user_collection.insert_one(user.model_dump(exclude_none=True))
    print(t1)
    return NoSQLUserList(id=str(t1.inserted_id), **user.model_dump())

@nosql_user_router.get("/{user_id}", response_model=NoSQLUserList)
async def get_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail={ "msg" : "user id not valid" })

    t1 = user_collection.find_one({ "_id": ObjectId(user_id) })

    if t1 is None:
        raise HTTPException(status_code=404, detail={ "msg": "No user found" })
    
    return NoSQLUserList(id=str(t1["_id"]), name=t1["name"], email=t1["email"])
