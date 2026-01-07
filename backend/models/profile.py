from dataclasses import dataclass
from datetime import datetime


@dataclass
class Profile:
    id: int
    user_id: int
    first_name: str
    last_name: str
    phone_number: str | None
    address: str | None
    preferences: str | None
    created_at: datetime
    updated_at: datetime