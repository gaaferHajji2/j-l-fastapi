from typing import Optional
from pydantic import BaseModel, Field

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    is_public: bool = Field(True, description="Whether the group is public")
