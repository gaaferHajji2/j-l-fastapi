from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: str

class UserList(UserCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class NoSQLUserList(UserCreate):
    id: str
    model_config = ConfigDict(from_attributes=True)