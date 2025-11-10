from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.orm import mapped_collection, Mapped, DeclarativeBase
from dotenv import find_dotenv, load_dotenv

import os
import datetime

load_dotenv(find_dotenv(filename='.env', raise_error_if_not_found=True), verbose=True)

engine = create_async_engine(os.environ.get('DATABASE_URL', ''), echo=True)