from pydantic import BaseModel

# This Is For Our Request Content From User
class UserPostIn(BaseModel):
    body: str

# This Is For Our Output Response For User
class UserPost(UserPostIn):
    id: int