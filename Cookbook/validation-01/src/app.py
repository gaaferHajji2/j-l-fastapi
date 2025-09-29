from fastapi import FastAPI

from schema.user_schema import UserList, User

app = FastAPI()

@app.post("/", response_model=UserList, status_code=200)
async def getUser(user: User):
    return UserList(id=0, **user.model_dump())