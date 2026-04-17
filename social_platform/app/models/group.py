from typing import List, Optional
from datetime import datetime
from app.core.database import Base
from app.models.user import User, user_group
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Group(Base):
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Many-to-many relationship with User
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_group,
        back_populates="groups"
    )
    
    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"