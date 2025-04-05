from contextlib import asynccontextmanager

from fastapi import FastAPI

import logging

from social_network.routes.post import router as post_router
from social_network.routes.comment import router as comment_router

from social_network.logging_conf import configure_logging

from social_network.database import database

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    configure_logging()

    await database.connect()

    logger.info("Database Connected Successfully")

    yield

    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(post_router, prefix="/post")

app.include_router(comment_router, prefix="/comment")