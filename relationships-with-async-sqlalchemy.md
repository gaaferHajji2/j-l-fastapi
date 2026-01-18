I'll create a comprehensive FastAPI example with all relationship types using async SQLAlchemy. This example includes a social media platform scenario.

## Project Structure
```
social_platform/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── errors.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── crud/
│   │   ├── __init__.py
│   │   └── user.py
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints/
│               ├── __init__.py
│               └── users.py
├── .env
└── requirements.txt
```

## 1. Dependencies (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
pydantic-extra-types==2.4.0
python-dotenv==1.0.0
email-validator==2.1.0
```

## 2. Configuration (app/core/config.py)
```python
from pydantic import EmailStr, PostgresDsn
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://user:password@localhost/social_platform"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Application
    APP_NAME: str = "Social Platform API"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

## 3. Database Setup (app/core/database.py)
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## 4. Custom Errors (app/core/errors.py)
```python
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error"""
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation related errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(message, code)


class NotFoundError(AppError):
    """Resource not found errors"""
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID {resource_id} not found"
        super().__init__(message, "NOT_FOUND_ERROR")


class ConflictError(AppError):
    """Conflict errors (duplicate, already exists)"""
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT_ERROR")


class RelationshipError(AppError):
    """Relationship related errors"""
    def __init__(self, message: str):
        super().__init__(message, "RELATIONSHIP_ERROR")


async def handle_validation_error(field: str, message: str):
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "code": f"VALIDATION_ERROR_{field.upper()}",
            "message": message,
            "field": field
        }
    )


async def handle_not_found_error(resource: str, resource_id: Any = None):
    message = f"{resource} not found"
    if resource_id:
        message = f"{resource} with ID {resource_id} not found"
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "NOT_FOUND_ERROR",
            "message": message,
            "resource": resource,
            "resource_id": str(resource_id)
        }
    )


async def handle_conflict_error(message: str):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "CONFLICT_ERROR",
            "message": message
        }
    )


async def handle_relationship_error(message: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "code": "RELATIONSHIP_ERROR",
            "message": message
        }
    )
```

## 5. Models (app/models/user.py)
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional
import enum
from datetime import datetime
from app.core.database import Base


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
    __tablename__ = "users"
    
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


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    location: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(200))
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # One-to-one relationship with User
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


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


class Comment(Base):
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Many-to-one relationship with User
    user: Mapped["User"] = relationship("User", back_populates="comments")
    
    # Many-to-one relationship with Post
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    
    # Self-referential relationship for nested comments
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side=[id],
        backref="replies",
        foreign_keys=[parent_id]
    )
    
    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, post_id={self.post_id})>"


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


# Many-to-many association table for post categories
post_categories = Table(
    'post_categories',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
)
```

## 6. Pydantic Schemas (app/schemas/user.py)
```python
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


# Base schemas
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v


class UserProfileBase(BaseModel):
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")


# Request schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "securepassword123"
            }
        }
    )


class UserProfileCreate(UserProfileBase):
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    status: Optional[UserStatus] = Field(None, description="User status")


class UserProfileUpdate(UserProfileBase):
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")


class FriendRequest(BaseModel):
    friend_id: int = Field(..., description="ID of the user to add as friend")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "friend_id": 2
            }
        }
    )


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    is_public: bool = Field(True, description="Whether the group is public")


# Response schemas
class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    date_of_birth: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    parent_id: Optional[int]
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    created_by: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: int
    is_active: bool
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserWithRelationsResponse(UserResponse):
    posts: List[PostResponse] = []
    friends: List["UserResponse"] = []
    groups: List[GroupResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class UserWithFriendsResponse(UserResponse):
    friends: List["UserResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


class UserWithPostsResponse(UserResponse):
    posts: List[PostResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class PostWithRelationsResponse(PostResponse):
    author: UserResponse
    comments: List[CommentResponse] = []
    categories: List[CategoryResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class GroupWithMembersResponse(GroupResponse):
    members: List[UserResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
```

## 7. CRUD Operations (app/crud/user.py)
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.user import User, UserProfile, Post, Comment, Group, Category, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserProfileCreate, UserProfileUpdate
from app.core.errors import NotFoundError, ConflictError, RelationshipError
import bcrypt


class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID with one-to-one profile"""
        result = await self.db.execute(
            select(User).options(selectinload(User.profile)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_with_relations(self, user_id: int) -> Optional[User]:
        """Get user with all relationships"""
        result = await self.db.execute(
            select(User).options(
                selectinload(User.profile),
                selectinload(User.posts),
                selectinload(User.friends),
                selectinload(User.groups),
                selectinload(User.comments)
            ).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(
            select(User).options(selectinload(User.profile)).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create user with one-to-one profile"""
        # Check for existing email
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise ConflictError(f"User with email {user_data.email} already exists")
        
        # Check for existing username
        existing_username = await self.get_user_by_username(user_data.username)
        if existing_username:
            raise ConflictError(f"User with username {user_data.username} already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        # Create profile
        profile = UserProfile(user=user)
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        # Check if user exists
        user = await self.get_user(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        # Check for email conflict if updating email
        if user_data.email and user_data.email != user.email:
            existing_email = await self.get_user_by_email(user_data.email)
            if existing_email:
                raise ConflictError(f"User with email {user_data.email} already exists")
        
        # Check for username conflict if updating username
        if user_data.username and user_data.username != user.username:
            existing_username = await self.get_user_by_username(user_data.username)
            if existing_username:
                raise ConflictError(f"User with username {user_data.username} already exists")
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        result = await self.db.execute(
            delete(User).where(User.id == user_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def update_profile(self, user_id: int, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        user = await self.get_user(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        if not user.profile:
            # Create profile if it doesn't exist
            user.profile = UserProfile(user_id=user_id, **profile_data.model_dump(exclude_unset=True))
        else:
            # Update existing profile
            update_data = profile_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user.profile, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user.profile
    
    # One-to-many relationship methods
    async def get_user_posts(self, user_id: int) -> List[Post]:
        user = await self.get_user(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        result = await self.db.execute(
            select(Post).where(Post.author_id == user_id).options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.categories)
            )
        )
        return result.scalars().all()
    
    async def create_post(self, user_id: int, title: str, content: str) -> Post:
        user = await self.get_user(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        post = Post(
            title=title,
            content=content,
            author_id=user_id
        )
        
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post
    
    # Many-to-many relationship methods (friends)
    async def add_friend(self, user_id: int, friend_id: int) -> User:
        if user_id == friend_id:
            raise RelationshipError("Cannot add yourself as a friend")
        
        user = await self.get_user_with_relations(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        friend = await self.get_user(friend_id)
        if not friend:
            raise NotFoundError("User", friend_id)
        
        # Check if already friends
        if friend in user.friends:
            raise ConflictError(f"User {friend_id} is already a friend")
        
        # Add bidirectional friendship
        user.friends.append(friend)
        friend.friends.append(user)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def remove_friend(self, user_id: int, friend_id: int) -> User:
        user = await self.get_user_with_relations(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        friend = await self.get_user_with_relations(friend_id)
        if not friend:
            raise NotFoundError("User", friend_id)
        
        # Check if they are friends
        if friend not in user.friends:
            raise RelationshipError(f"User {friend_id} is not in your friends list")
        
        # Remove bidirectional friendship
        user.friends.remove(friend)
        friend.friends.remove(user)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_friends(self, user_id: int) -> List[User]:
        user = await self.get_user_with_relations(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        return user.friends
    
    # Many-to-many relationship methods (groups)
    async def join_group(self, user_id: int, group_id: int) -> User:
        user = await self.get_user_with_relations(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        result = await self.db.execute(
            select(Group).options(selectinload(Group.members)).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise NotFoundError("Group", group_id)
        
        # Check if already in group
        if group in user.groups:
            raise ConflictError(f"User is already a member of group {group_id}")
        
        user.groups.append(group)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def leave_group(self, user_id: int, group_id: int) -> User:
        user = await self.get_user_with_relations(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        result = await self.db.execute(
            select(Group).options(selectinload(Group.members)).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise NotFoundError("Group", group_id)
        
        # Check if in group
        if group not in user.groups:
            raise RelationshipError(f"User is not a member of group {group_id}")
        
        user.groups.remove(group)
        await self.db.commit()
        await self.db.refresh(user)
        return user


class PostCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_post_with_relations(self, post_id: int) -> Optional[Post]:
        result = await self.db.execute(
            select(Post).options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.categories)
            ).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
    
    async def add_category_to_post(self, post_id: int, category_id: int) -> Post:
        post = await self.get_post_with_relations(post_id)
        if not post:
            raise NotFoundError("Post", post_id)
        
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise NotFoundError("Category", category_id)
        
        # Check if category already added
        if category in post.categories:
            raise ConflictError(f"Category {category_id} is already added to post {post_id}")
        
        post.categories.append(category)
        await self.db.commit()
        await self.db.refresh(post)
        return post
```

## 8. API Endpoints (app/api/v1/endpoints/users.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.crud.user import UserCRUD, PostCRUD
from app.schemas.user import (
    UserCreate, UserResponse, UserWithRelationsResponse, 
    UserWithFriendsResponse, UserWithPostsResponse,
    UserUpdate, UserProfileUpdate, FriendRequest,
    PostWithRelationsResponse
)
from app.core.errors import (
    handle_not_found_error, handle_conflict_error,
    handle_validation_error, handle_relationship_error
)
from app.models.user import UserStatus

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user with one-to-one profile"""
    try:
        crud = UserCRUD(db)
        user = await crud.create_user(user_data)
        return user
    except ValueError as e:
        await handle_validation_error("username", str(e))
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "CONFLICT_ERROR":
                await handle_conflict_error(str(e))
            elif e.code.startswith("VALIDATION_ERROR"):
                field = e.code.replace("VALIDATION_ERROR_", "").lower()
                await handle_validation_error(field, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )


@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of users"""
    crud = UserCRUD(db)
    users = await crud.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserWithRelationsResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID with all relationships"""
    crud = UserCRUD(db)
    user = await crud.get_user_with_relations(user_id)
    
    if not user:
        await handle_not_found_error("User", user_id)
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user information"""
    try:
        crud = UserCRUD(db)
        user = await crud.update_user(user_id, user_data)
        return user
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "NOT_FOUND_ERROR":
                await handle_not_found_error("User", user_id)
            elif e.code == "CONFLICT_ERROR":
                await handle_conflict_error(str(e))
        raise


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user"""
    crud = UserCRUD(db)
    deleted = await crud.delete_user(user_id)
    
    if not deleted:
        await handle_not_found_error("User", user_id)


@router.put("/{user_id}/profile", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    profile_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user profile (one-to-one relationship)"""
    try:
        crud = UserCRUD(db)
        await crud.update_profile(user_id, profile_data)
        
        # Return updated user
        user = await crud.get_user(user_id)
        return user
    except Exception as e:
        if hasattr(e, 'code') and e.code == "NOT_FOUND_ERROR":
            await handle_not_found_error("User", user_id)
        raise


@router.get("/{user_id}/posts", response_model=List[PostWithRelationsResponse])
async def read_user_posts(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all posts by a user (one-to-many relationship)"""
    crud = UserCRUD(db)
    posts = await crud.get_user_posts(user_id)
    return posts


@router.post("/{user_id}/posts", response_model=PostWithRelationsResponse, status_code=status.HTTP_201_CREATED)
async def create_user_post(
    user_id: int,
    title: str = Query(..., min_length=1, max_length=200, description="Post title"),
    content: str = Query(..., min_length=1, description="Post content"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post for a user (one-to-many relationship)"""
    try:
        crud = UserCRUD(db)
        post = await crud.create_post(user_id, title, content)
        
        # Return post with relations
        post_crud = PostCRUD(db)
        return await post_crud.get_post_with_relations(post.id)
    except Exception as e:
        if hasattr(e, 'code') and e.code == "NOT_FOUND_ERROR":
            await handle_not_found_error("User", user_id)
        raise


@router.post("/{user_id}/friends", response_model=UserWithFriendsResponse)
async def add_friend(
    user_id: int,
    friend_request: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add a friend (many-to-many relationship)"""
    try:
        crud = UserCRUD(db)
        user = await crud.add_friend(user_id, friend_request.friend_id)
        return user
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "NOT_FOUND_ERROR":
                resource = "User" if "User" in str(e) else "Friend"
                resource_id = friend_request.friend_id if "Friend" in str(e) else user_id
                await handle_not_found_error(resource, resource_id)
            elif e.code == "CONFLICT_ERROR":
                await handle_conflict_error(str(e))
            elif e.code == "RELATIONSHIP_ERROR":
                await handle_relationship_error(str(e))
        raise


@router.delete("/{user_id}/friends/{friend_id}", response_model=UserWithFriendsResponse)
async def remove_friend(
    user_id: int,
    friend_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove a friend (many-to-many relationship)"""
    try:
        crud = UserCRUD(db)
        user = await crud.remove_friend(user_id, friend_id)
        return user
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "NOT_FOUND_ERROR":
                resource = "User" if "User" in str(e) else "Friend"
                resource_id = friend_id if "Friend" in str(e) else user_id
                await handle_not_found_error(resource, resource_id)
            elif e.code == "RELATIONSHIP_ERROR":
                await handle_relationship_error(str(e))
        raise


@router.get("/{user_id}/friends", response_model=UserWithFriendsResponse)
async def get_friends(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all friends of a user"""
    crud = UserCRUD(db)
    user = await crud.get_user_with_relations(user_id)
    
    if not user:
        await handle_not_found_error("User", user_id)
    
    return user


@router.post("/{user_id}/groups/{group_id}", response_model=UserWithRelationsResponse)
async def join_group(
    user_id: int,
    group_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Join a group (many-to-many relationship)"""
    try:
        crud = UserCRUD(db)
        user = await crud.join_group(user_id, group_id)
        return user
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "NOT_FOUND_ERROR":
                resource = "User" if "User" in str(e) else "Group"
                resource_id = group_id if "Group" in str(e) else user_id
                await handle_not_found_error(resource, resource_id)
            elif e.code == "CONFLICT_ERROR":
                await handle_conflict_error(str(e))
            elif e.code == "RELATIONSHIP_ERROR":
                await handle_relationship_error(str(e))
        raise


@router.delete("/{user_id}/groups/{group_id}", response_model=UserWithRelationsResponse)
async def leave_group(
    user_id: int,
    group_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Leave a group (many-to-many relationship)"""
    try:
        crud = UserCRUD(db)
        user = await crud.leave_group(user_id, group_id)
        return user
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "NOT_FOUND_ERROR":
                resource = "User" if "User" in str(e) else "Group"
                resource_id = group_id if "Group" in str(e) else user_id
                await handle_not_found_error(resource, resource_id)
            elif e.code == "RELATIONSHIP_ERROR":
                await handle_relationship_error(str(e))
        raise


@router.post("/posts/{post_id}/categories/{category_id}", response_model=PostWithRelationsResponse)
async def add_category_to_post(
    post_id: int,
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Add a category to a post (many-to-many relationship)"""
    try:
        crud = PostCRUD(db)
        post = await crud.add_category_to_post(post_id, category_id)
        return post
    except Exception as e:
        if hasattr(e, 'code'):
            if e.code == "NOT_FOUND_ERROR":
                resource = "Post" if "Post" in str(e) else "Category"
                resource_id = category_id if "Category" in str(e) else post_id
                await handle_not_found_error(resource, resource_id)
            elif e.code == "CONFLICT_ERROR":
                await handle_conflict_error(str(e))
        raise
```

## 9. Main Application (app/main.py)
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import create_tables, engine
from app.api.v1.endpoints import users
from app.core.errors import AppError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await create_tables()
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Global exception handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "message": exc.message
        }
    )


# Include routers
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Social Platform API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

## 10. Environment Variables (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/social_platform

# Application
DEBUG=true
APP_NAME="Social Platform API"

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

## Key Features Demonstrated:

1. **All Relationship Types:**
   - One-to-one: User ↔ UserProfile
   - One-to-many: User ↔ Posts, User ↔ Comments, Post ↔ Comments
   - Many-to-many: User ↔ User (friends), User ↔ Group, Post ↔ Category

2. **Pydantic Features:**
   - Email validation with `EmailStr`
   - Request/Response schemas with proper validation
   - Environment configuration with `pydantic-settings`
   - ConfigDict for ORM mode

3. **Error Handling:**
   - Custom error classes with specific codes
   - Detailed error messages for each state
   - Proper HTTP status codes
   - Field-specific validation errors

4. **Async Operations:**
   - Async SQLAlchemy for database operations
   - Proper session management with context managers
   - Efficient relationship loading with `selectinload`

## Running the Application:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update `.env` file

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Access the API documentation at `http://localhost:8000/docs`

This comprehensive example demonstrates best practices for handling relationships in FastAPI with async SQLAlchemy, including proper error handling, validation, and clean architecture.