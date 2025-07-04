import os

from contextlib import asynccontextmanager

from fastapi import FastAPI

from migration.db import init_db

from migration.models.songs import Song

from migration.routes.song import router

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()

    yield

app = FastAPI(lifespan=lifespan)

@app.get('/hello')
async def hello():
    return { 
        "msg": "Hello World With SQLModel And Migration Example" 
    }

app.include_router(router=router)