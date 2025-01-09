from fastapi import APIRouter, HTTPException

from models.comment import UserCommentIn, UserComment, UserPostWithComments

from routes.post import find_post

router = APIRouter()

comment_table = {}

@router.post("/", response_model=UserComment, status_code=201)
async def create_comment(comment: UserCommentIn):
    data = comment.model_dump()

    post = find_post(data['post_id'])
    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")

    last_record_id = len(comment_table)

    new_comment = {**data, "id": last_record_id}

    comment_table[last_record_id] = new_comment

    return new_comment

@router.get("/", response_model=list[UserComment])
async def get_all_comments():
    return list(comment_table.values())

@router.get("/{post_id}/comment", response_model=list[UserComment])
async def get_post_comments(post_id: int):
    return [comment for comment in comment_table.values() if comment["post_id" ]== post_id]

@router.get("/{post_id}/post-with-comments", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)

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