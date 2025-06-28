import os

from contextlib import asynccontextmanager

from fastapi import FastAPI

from migration.db import init_db

from migration.models.songs import Song

from migration.routes.song import router

@asynccontextmanager
async def lifespan(app: FastAPI):

    # load_dotenv(find_dotenv())

    await init_db()

    # print("Database Connection OK!")

    # DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

    # d1 = os.getenv("DATABASE_URL")

    # print("The Database URL is: ", DATABASE_URL);

    # print("d1 is: ", d1)

    yield

app = FastAPI(lifespan=lifespan)

@app.get('/hello')
async def hello():
    return { 
        "msg": "Hello World With SQLModel And Migration Example" 
    }

app.include_router(router=router)