import logging

from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from enum import Enum

import sqlalchemy

from social_network.database import posts_table, likes_table, database

from social_network.models.post import UserPost, UserPostIn, UserPostWithLikes

from social_network.models.user import User

from social_network.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)

# print(__name__)

# @router.get("/")
# async def getHelloMessage():
#     return {"Message": "Hello"}

# post_table = {}


select_post_and_likes = (
    sqlalchemy.select(
        posts_table, 
        # .label('likes') --> Is Similar To Use: AS-Keyword
        sqlalchemy.func.count(likes_table.c.id).label("likes"),
    
    )\
    .select_from(posts_table.outerjoin(likes_table))\
    .group_by(posts_table.c.id)
)


async def find_post(post_id: int):
    query = posts_table.select().where(posts_table.c.id == post_id)

    logger.debug(f"The Query For Get Post By Id: {query}")

    return await database.fetch_one(query)

@router.post("/", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]):

    # In This Way We Protect The Endpoint From Un-Authenticated Requests
    # current_user: User = await get_current_user(await oauth2_schema(request=request))

    # if current_user.confirmed is None or not current_user.confirmed:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Can't Create Post, Please Confirm URL"
    #     )

    data = {**post.model_dump(), "user_id": current_user.id}

    query = posts_table.insert().values(data)

    # logger.debug(f"The Query For Create Post Is: {query}", extra={"email": "jafar.loka@loka.com"})
    logger.debug(f"The Query For Create Post Is: {query}")

    last_id = await database.execute(query)

    return  {**data, "id": last_id}

class PostSorting(str, Enum):
    new = "new"

    old = "old"

    most_likes = "most_likes"

@router.get("/", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    # return post_table.values()
    # OR We Can Use

    print(f"The Sorting Is: {sorting}")

    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(posts_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(posts_table.c.id.asc())
    else:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    # query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(f"The Query For Get All Posts Is: {query}")

    return await database.fetch_all(query)