from dotenv import load_dotenv, find_dotenv

import os

from sqlmodel import SQLModel, create_engine, Session

load_dotenv(find_dotenv(filename='migration/.env', raise_error_if_not_found=True))

print("The Dot Env Is: ", find_dotenv(filename='migration/.env', raise_error_if_not_found=True))

DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

# d1 = os.getenv("DATABASE_URL")

# print("The Database URL is: ", DATABASE_URL);

# print("d1 is: ", d1)

engine = create_engine(url=DATABASE_URL, echo=True)

async def init_db():
    SQLModel.metadata.create_all(bind=engine)

async def get_session():
    with Session(bind=engine) as session:
        yield session