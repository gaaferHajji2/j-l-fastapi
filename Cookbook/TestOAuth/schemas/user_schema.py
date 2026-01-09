from pydantic import BaseModel, EmailStr, constr, ConfigDict

class UserSchemaRes(BaseModel):
    id: int
    name: constr(min_length=1, max_length=255) # type: ignore
    email: EmailStr
    model_config = ConfigDict(from_attributes = True)

class UserSchemaReq(BaseModel):
    name: constr(min_length=1, max_length=255) # type: ignore
    email: EmailStr
    password: constr(min_length=2, max_length=80)# type: ignore