from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from fastapi.exception_handlers import http_exception_handler

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

@app.exception_handler(HTTPException)
async def http_exception_handler_logger(request: Request, exc: HTTPException):
    logger.error(f"HTTPException With Status Code: {exc.status_code}, Details: {exc.detail}")

    return await http_exception_handler(request, exc)