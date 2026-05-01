from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user_schema import UserResponse
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostWithRelationsResponse(PostResponse):
    author: UserResponse
    comments: List["CommentResponse"] = []
    categories: List["CategoryResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)
