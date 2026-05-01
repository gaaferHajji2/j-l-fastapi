from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user_crud import UserCRUD
from app.crud.post_crud import PostCRUD
from app.schemas.user_schema import UserResponse, UserCreate, UserWithRelationsResponse, UserUpdate, UserWithFriendsResponse
from app.schemas.user_profile_schema import UserProfileUpdate
from app.schemas.post_schema import PostWithRelationsResponse
from app.schemas.friend_schema import FriendRequest
from app.core.database import get_db
from app.core.errors import handle_validation_error, handle_conflict_error, handle_not_found_error, handle_relationship_error

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
