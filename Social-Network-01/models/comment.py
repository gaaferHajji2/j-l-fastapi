from pydantic import BaseModel, ConfigDict

from models.post import UserPost

class UserCommentIn(BaseModel):
    body: str
    post_id: int

class UserComment(UserCommentIn):

    model_config = ConfigDict(from_attributes=True)

    id: int

class UserPostWithComments(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    post: UserPost
    comments: list[UserComment]