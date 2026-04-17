from typing import List
from datetime import datetime
from app.core.database import Base
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, relationship, Mapped
from app.models.user import User
from app.models.comment import Comment
from app.models.category import Category

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Many-to-one relationship with User
    author: Mapped["User"] = relationship("User", back_populates="posts")
    
    # One-to-many relationship with Comment
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    
    # Many-to-many relationship with Category
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary="post_categories",
        back_populates="posts"
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, author_id={self.author_id})>"