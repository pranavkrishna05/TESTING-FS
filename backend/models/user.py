from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    login_attempts: int = 0
    is_locked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('password')
    def validate_password(cls, v: str) -> str:
        # Password must meet security criteria: minimum 8 characters, at least one uppercase, one lowercase, one digit, and one special character
        import re
        if len(v) < 8 or not re.search(r'[A-Z]', v) or not re.search(r'[a-z]', v) or not re.search(r'\d', v) or not re.search(r'[@$!%*?&]', v):
            raise ValueError('Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.')
        return v

    class Config:
        orm_mode = True
        validate_assignment = True