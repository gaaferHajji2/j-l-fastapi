from typing import Optional

from pydantic import BaseModel, ConfigDict

# This Is For Our Request Content From User
class UserPostIn(BaseModel):
    body: str

# This Is For Our Output Response For User
class UserPost(UserPostIn):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    image_url: Optional[str] = None

class UserPostWithLikes(UserPost):
    model_config = ConfigDict(from_attributes=True)

    likes: int