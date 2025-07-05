from dotenv import load_dotenv, find_dotenv

import os

# from sqlmodel import SQLModel, create_engine, Session
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv(find_dotenv(filename='migration/.env', raise_error_if_not_found=True))

# print("The Dot Env Is: ", find_dotenv(filename='migration/.env', raise_error_if_not_found=True))

DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

# d1 = os.getenv("DATABASE_URL")

# print("The Database URL is: ", DATABASE_URL);

# print("d1 is: ", d1)

engine = create_async_engine(url=DATABASE_URL, echo=True, future=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # SQLModel.metadata.create_all(bind=engine)

async def get_session() -> AsyncGenerator[AsyncSession, None]:

    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session