from typing import Optional, List
from datetime import datetime
from app.core.database import Base
from sqlalchemy import Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.post import Post

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Many-to-many relationship with Post
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        secondary="post_categories",
        back_populates="categories"
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"