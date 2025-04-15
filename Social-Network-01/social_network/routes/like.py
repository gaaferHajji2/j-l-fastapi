from fastapi import APIRouter, Depends, HTTPException, status

from typing import Annotated

import logging 

from social_network.security import get_current_user

from social_network.database import likes_table, posts_table, users_table, database

from social_network.models.user import User

from social_network.models.likes import PostLikeIn, PostLike

from social_network.routes.post import find_post

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post('/like', response_model=PostLike, status_code=201)
async def like_post(like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Create Like For Post With Id: {like.post_id}")

    post = await find_post(like.post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post Not Found With Id: {like.post_id}"
        )
    
    data = {**like.model_dump(), "user_id": current_user.id}

    query = likes_table.insert().values(data)

    logger.debug(f"The Query For Creating Like: {query}")

    result = await database.execute(query)

    return {**data, "id": result}