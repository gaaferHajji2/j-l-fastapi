from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from fastapi.exception_handlers import http_exception_handler

import logging

from asgi_correlation_id import CorrelationIdMiddleware

from social_network.routes.post import router as post_router
from social_network.routes.comment import router as comment_router
from social_network.routes.user import router as user_router
from social_network.routes.like import router as like_router
from social_network.routes.upload_files import router as upload_router

from social_network.logging_conf import configure_logging

from social_network.database import database

# from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    configure_logging()

    await database.connect()

    logger.info("Database Connected Successfully")

    yield

    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router, prefix="/post")

app.include_router(comment_router, prefix="/comment")

app.include_router(user_router, prefix='/user')

app.include_router(like_router)

app.include_router(upload_router)

@app.exception_handler(HTTPException) # In This Way We Can Pass:
# The Exception Class OR The Status Code That We Want To Handle
# We Return Any Class That Inherit From Response-Class Like: JSONResponse
async def http_exception_handler_logger(request: Request, exc: HTTPException):
    logger.error(f"HTTPException With Status Code: {exc.status_code}, Details: {exc.detail}")

    return await http_exception_handler(request, exc)