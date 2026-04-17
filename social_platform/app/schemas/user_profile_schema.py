from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class UserProfileBase(BaseModel):
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")

class UserProfileCreate(UserProfileBase):
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")