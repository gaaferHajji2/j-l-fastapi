from fastapi import APIRouter, HTTPException

from models.comment import UserCommentIn, UserComment, UserPostWithComments

from routes.post import find_post

from database import comments_table, database

router = APIRouter()

@router.post("/", response_model=UserComment, status_code=201)
async def create_comment(comment: UserCommentIn):
    data = comment.model_dump()

    post = await find_post(data['post_id'])

    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    query = comments_table.insert().values(data)

    last_id = await database.execute(query)

    return {**data, "id": last_id}

@router.get("/", response_model=list[UserComment])
async def get_all_comments():
    query = comments_table.select()

    return await database.fetch_all(query)

@router.get("/{post_id}/comment", response_model=list[UserComment])
async def get_post_comments(post_id: int):
    post = await find_post(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    query = database.select().where(comments_table.c.post_id == post_id)

    return await database.fetch_all(query)

@router.get("/{post_id}/post-with-comments", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    # return {
    #     "post": post,
    #     "comments": [comment for comment in comment_table.values() if comment["post_id" ]== post_id]
    # }

    return {
        "post": post,
        "comments": await get_post_comments(post_id=post_id)
    }