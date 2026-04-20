from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
