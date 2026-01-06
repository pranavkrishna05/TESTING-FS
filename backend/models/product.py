from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    description: str
    category_id: int
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('name')
    def name_must_be_unique(cls, v: str) -> str:
        if not v:
            raise ValueError('Product name cannot be empty')
        return v

    @validator('price')
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Product price must be a positive number')
        return v

    @validator('description')
    def description_cannot_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError('Product description cannot be empty')
        return v

    class Config:
        orm_mode = True
        validate_assignment = True