from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    is_public: bool = Field(True, description="Whether the group is public")

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    created_by: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
