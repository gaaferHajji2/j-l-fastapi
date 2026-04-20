from pydantic import BaseModel, ConfigDict, Field

class FriendRequest(BaseModel):
    friend_id: int = Field(..., description="ID of the user to add as friend")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "friend_id": 2
            }
        }
    )
