from fastapi import FastAPI

from routes.post import router as post_router

app = FastAPI()

app.include_router(post_router, prefix="/post")