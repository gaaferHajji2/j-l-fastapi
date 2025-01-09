from pydantic import BaseModel

from models.post import UserPost

class UserCommentIn(BaseModel):
    body: str
    post_id: int

class UserComment(UserCommentIn):
    id: int

class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[UserComment]