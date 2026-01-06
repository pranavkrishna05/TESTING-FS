from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PasswordReset(BaseModel):
    id: Optional[int] = None
    user_id: int
    token: str
    expires_at: datetime
    used: bool = False

    class Config:
        orm_mode = True
        validate_assignment = True