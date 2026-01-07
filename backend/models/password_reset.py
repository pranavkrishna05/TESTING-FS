from dataclasses import dataclass
from datetime import datetime


@dataclass
class PasswordReset:
    id: int
    user_id: int
    token: str
    expires_at: datetime
    is_used: bool
    created_at: datetime