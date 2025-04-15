import logging

from fastapi import APIRouter, Request, Depends

from typing import Annotated

import sqlalchemy

from social_network.database import posts_table, likes_table, database

from social_network.models.post import UserPost, UserPostIn

from social_network.models.user import User

from social_network.security import get_current_user, oauth2_schema

router = APIRouter()

logger = logging.getLogger(__name__)

# print(__name__)

# @router.get("/")
# async def getHelloMessage():
#     return {"Message": "Hello"}

# post_table = {}



async def find_post(post_id: int):
    query = posts_table.select().where(posts_table.c.id == post_id)

    logger.debug(f"The Query For Get Post By Id: {query}")

    return await database.fetch_one(query)

@router.post("/", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]):

    # In This Way We Protect The Endpoint From Un-Authenticated Requests
    # current_user: User = await get_current_user(await oauth2_schema(request=request))

    data = {**post.model_dump(), "user_id": current_user.id}

    query = posts_table.insert().values(data)

    # logger.debug(f"The Query For Create Post Is: {query}", extra={"email": "jafar.loka@loka.com"})
    logger.debug(f"The Query For Create Post Is: {query}")

    last_id = await database.execute(query)

    return  {**data, "id": last_id}


@router.get("/", response_model=list[UserPost])
async def get_all_posts():
    # return post_table.values()
    # OR We Can Use
    query = posts_table.select()

    logger.debug(f"The Query For Get All Posts Is: {query}")

    return await database.fetch_all(query)