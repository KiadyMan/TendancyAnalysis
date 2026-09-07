from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class TrendSchema(BaseModel):
    brand: str
    price: float
    sale_date: date
    quantity: int
    region: Optional[str] = None
    revenue: float
    growth_rate_pct: float
    trend: str
    created_at: datetime

    class Config:
        from_attributes = True