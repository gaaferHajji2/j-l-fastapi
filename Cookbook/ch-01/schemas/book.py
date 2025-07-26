from pydantic import BaseModel, Field

from typing import Optional

class Book(BaseModel):
    title: str
    author: str
    year: Optional[int|str] = None

class AdvancedBook(BaseModel):
    title: str = Field(..., min_length=2, max_length=250, description="Title must be at least 2-chars")
    author: str = Field(..., min_length=5, max_length=255, description="author must be at least 5-chars")
    year: Optional[int|str] = Field(default=0, lt=200000, ge=2000, description="year must be between 2000 && 20000")