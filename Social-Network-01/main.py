from fastapi import FastAPI

from routes.post import router as post_router
from routes.comment import router as comment_router

app = FastAPI()

app.include_router(post_router, prefix="/post")

app.include_router(comment_router, prefix="/comment")