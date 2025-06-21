from pydantic import BaseModel, ConfigDict

from social_network.models.post import UserPostWithLikes



class UserCommentIn(BaseModel):
    body: str
    post_id: int

class UserComment(UserCommentIn):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

class UserPostWithComments(BaseModel):

    post: UserPostWithLikes
    comments: list[UserComment]