from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user_crud import UserCRUD
from app.schemas.user_schema import UserResponse, UserCreate
from app.core.database import get_db
from app.core.errors import handle_validation_error, handle_conflict_error

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
