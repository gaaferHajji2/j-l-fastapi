from fastapi import APIRouter, HTTPException, status

import logging

from passlib.hash import pbkdf2_sha256
 
from social_network.models.user import UserIn

from social_network.security import get_user_by_email

from social_network.database import database, users_table

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post('/register', status_code=201)
async def register(user: UserIn):
    t1 = await get_user_by_email(user.email)

    if t1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User Already Exists With That Email"
        )
    
    query = users_table.insert().values(
        email=user.email, 
        password=pbkdf2_sha256.hash(user.password)
    )

    logger.debug(f"The Query For Creating User: {query}")

    result = await database.execute(query)

    return {"msg": "User Created Successfully", "id": result}