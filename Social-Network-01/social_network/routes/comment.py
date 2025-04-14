import logging

from fastapi import APIRouter, HTTPException, Request, Depends

from typing import Annotated

from social_network.models.comment import UserCommentIn, UserComment, UserPostWithComments

from social_network.routes.post import find_post

from social_network.database import comments_table, database

from social_network.models.user import User

from social_network.security import get_current_user, oauth2_schema

router = APIRouter()

logger = logging.getLogger(__name__)

# print(__name__)

@router.post("/", response_model=UserComment, status_code=201)
async def create_comment(comment: UserCommentIn, current_user: Annotated[User, Depends(get_current_user)]):

    # current_user: User = await get_current_user(await oauth2_schema(request=request))

    data = comment.model_dump()

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
    post = await find_post(post_id)

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