from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Session(BaseModel):
    id: Optional[int] = None
    user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    class Config:
        orm_mode = True
        validate_assignment = True