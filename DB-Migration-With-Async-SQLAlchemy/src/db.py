from dotenv import load_dotenv

import os
import datetime
from typing import AsyncGenerator

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        datetime.datetime : DateTime(timezone=True)
    }

engine = create_async_engine(os.environ.get("DATABASE_URL", ""), echo=True)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session