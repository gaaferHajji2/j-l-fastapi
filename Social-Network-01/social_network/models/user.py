from pydantic import BaseModel

class User(BaseModel):
    id: int | None = None
    email: str
    confirmed: bool = False

class UserIn(User):
    password: str