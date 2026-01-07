from dataclasses import dataclass
from datetime import datetime


@dataclass
class Account:
    id: int
    user_id: int
    username: str
    created_at: datetime
    updated_at: datetime