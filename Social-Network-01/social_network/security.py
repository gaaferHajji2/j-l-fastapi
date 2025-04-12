import logging

from passlib.context import CryptContext

from social_network.database import database, users_table

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hash: str):
    return pwd_context.verify(password, hash)

async def get_user_by_email(email: str):

    logger.debug("Fetching Users Data By Email", extra={"email": email})

    query = users_table.select().filter(users_table.c.email == email)

    logging.debug(f"The Query To Get User By Email Is: {query}")

    result = await database.fetch_one(query)

    if result:
        return result