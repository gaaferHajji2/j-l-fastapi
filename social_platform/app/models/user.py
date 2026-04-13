from typing import Optional, List
from datetime import datetime
import enum
from app.core.database import Base
from sqlalchemy import Table, Integer, Column, ForeignKey, func, DateTime, Boolean, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Many-to-many association table for user friendships
user_friendship = Table(
    'user_friendship',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
)

# Many-to-many association table for user group memberships
user_group = Table(
    'user_group',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    Column('is_admin', Boolean, default=False),
)

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # One-to-one relationship with UserProfile
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # One-to-many relationship with Post (user has many posts)
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    
    # One-to-many relationship with Comment (user has many comments)
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    
    # Many-to-many relationship with self (friends)
    friends: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_friendship,
        primaryjoin=id == user_friendship.c.user_id,
        secondaryjoin=id == user_friendship.c.friend_id,
        backref="friend_of",
        lazy="selectin"
    )
    
    # Many-to-many relationship with Group
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary=user_group,
        back_populates="members"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"