from typing import AsyncGenerator
from sqlalchemy import DateTime, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from sqlalchemy.orm import DeclarativeBase

import os

import datetime

from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(raise_error_if_not_found=True), verbose=True)

class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    type_annotation_map = {
        datetime.datetime : DateTime(timezone=True)
    }

# print(f"The DATABASE_URL is: {os.environ.get('DATABASE_URL', 'NULL')}")

engine = create_async_engine(os.environ.get("DATABASE_URL", ''), echo = True)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
