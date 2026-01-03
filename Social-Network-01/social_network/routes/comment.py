import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
import sqlalchemy

from social_network.models.comment import UserCommentIn, UserComment, UserPostWithComments
from social_network.routes.post import find_post
from social_network.database import comments_table, posts_table, likes_table, database
from social_network.models.user import User
from social_network.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)
# print(__name__)
select_post_and_likes = (
    sqlalchemy.select(
        posts_table, 
        # .label('likes') --> Is Similar To Use: AS-Keyword
        sqlalchemy.func.count(likes_table.c.id).label("likes"),
    
    )\
    .select_from(posts_table.outerjoin(likes_table))\
    .group_by(posts_table.c.id)
)

@router.post("/", response_model=UserComment, status_code=201)
async def create_comment(comment: UserCommentIn, current_user: Annotated[User, Depends(get_current_user)]):
    # current_user: User = await get_current_user(await oauth2_schema(request=request))
    data = {**comment.model_dump(), "user_id": current_user.id}
    post = await find_post(data['post_id'])
    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    query = comments_table.insert().values(data)
    logger.debug(f"The Query For Create Comment Is: {query}")
    last_id = await database.execute(query)
    return {**data, "id": last_id}

@router.get("/", response_model=list[UserComment])
async def get_all_comments():
    query = comments_table.select()
    logger.debug(f"The Query For Get All Comments Is: {query}")
    return await database.fetch_all(query)

@router.get("/{post_id}/comment", response_model=list[UserComment])
async def get_post_comments(post_id: int):
    post = await find_post(post_id)
    if post is None:
        # logger.error(f"Post Not Found For Get Comments With Id: {post_id}")
        raise HTTPException(status_code=404, detail=f"Post Not Found For Get Post Comments With Id: {post_id}")
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    logger.debug(f"The Query For Get Post Comments Is: {query}")
    return await database.fetch_all(query)

@router.get("/{post_id}/post-with-comments", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    # post = await find_post(post_id)
    query = select_post_and_likes.where(posts_table.c.id == post_id)
    logger.debug(f"The Query For Getting Post, With Likes And Comments: {query}")
    post = await database.fetch_one(query)
    if post is None:
        # logger.error(f"Post Not Found For Get Post With Comments With Id: {post_id}")
        raise HTTPException(status_code=404, detail=f"Post Not Found For Get Post With Its Comments With Id: {post_id}")
    # return {
    #     "post": post,
    #     "comments": [comment for comment in comment_table.values() if comment["post_id" ]== post_id]
    # }
    return {
        "post": post,
        "comments": await get_post_comments(post_id=post_id)
    }