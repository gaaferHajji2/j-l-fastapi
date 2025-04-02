from fastapi import APIRouter

from database import posts_table, database

from models.post import UserPost, UserPostIn

router = APIRouter()

# @router.get("/")
# async def getHelloMessage():
#     return {"Message": "Hello"}

# post_table = {}

async def find_post(post_id: int):
    query = posts_table.select().where(posts_table.c.id == post_id)
    return await database.fetch_one(query)

@router.post("/", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()

    query = posts_table.insert().values(data)

    last_id = await database.execute(query)

    return  {**data, "id": last_id}


@router.get("/", response_model=list[UserPost])
async def get_all_posts():
    # return post_table.values()
    # OR We Can Use
    query = posts_table.select()
    return await database.fetch_all(query)