from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    id: int
    name: str
    description: str | None
    parent_id: int | None
    created_at: datetime
    updated_at: datetime