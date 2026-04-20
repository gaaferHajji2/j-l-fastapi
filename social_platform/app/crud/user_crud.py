from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.post import Post
from app.models.group import Group
from app.schemas.user_schema import UserCreate, UserUpdate
from app.schemas.user_profile_schema import UserProfileUpdate
from app.core.errors import ConflictError, NotFoundError, RelationshipError

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
