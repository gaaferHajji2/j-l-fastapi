from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes.post import router as post_router
from routes.comment import router as comment_router

from database import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(post_router, prefix="/post")

app.include_router(comment_router, prefix="/comment")