from beanie import Document
from datetime import date, datetime
from pydantic import Field
from typing import Optional


class Trend(Document):
    product: Optional[str] = None
    brand: str
    price: float
    sale_date: date
    quantity: int
    region: Optional[str] = None
    ram: Optional[str] = None
    rom: Optional[str] = None
    revenue: float
    prev_quantity: int
    growth_rate_pct: float
    trend: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "trends"