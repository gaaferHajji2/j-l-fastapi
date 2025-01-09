from fastapi import APIRouter

from models.post import UserPost, UserPostIn

router = APIRouter()

# @router.get("/")
# async def getHelloMessage():
#     return {"Message": "Hello"}

post_table = {}

@router.post("/", response_model=UserPost)
async def create_post(post: UserPostIn):
    data = post.model_dump()

    last_record_id = len(post_table)

    new_post = {**data, "id": last_record_id}

    post_table[last_record_id] = new_post

    return new_post


@router.get("/", response_model=list[UserPost])
async def get_all_posts():
    # return post_table.values()
    # OR We Can Use
    return list(post_table.values())