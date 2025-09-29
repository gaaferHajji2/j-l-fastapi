from fastapi import FastAPI

from routes.users import users_router
from routes.nosql_users import nosql_user_router

app = FastAPI()

app.include_router(users_router, prefix='/users')

app.include_router(nosql_user_router, prefix='/nosql-users')