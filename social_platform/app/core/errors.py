from fastapi import HTTPException, status
from typing import Any, Optional

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