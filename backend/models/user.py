from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        validate_assignment = True