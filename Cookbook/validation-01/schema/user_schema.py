from pydantic import BaseModel, EmailStr, constr, field_validator

class User(BaseModel):
    name: constr(min_length=2, max_length=50) # type: ignore
    email: EmailStr
    age: int

    @field_validator('age')
    def validate_age(cls, value):
        if value < 18 or value > 100:
            raise ValueError("Age must be between 18 and 100")
        return value

class UserList(User):
    id: int