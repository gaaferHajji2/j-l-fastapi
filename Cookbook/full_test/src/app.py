from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from full_test.db import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/home', status_code=status.HTTP_200_OK)
async def get_home():
    return { "home": "Main Page - Home" }