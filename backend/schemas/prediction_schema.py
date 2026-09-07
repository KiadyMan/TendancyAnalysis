from pydantic import BaseModel
from datetime import datetime


class PredictionSchema(BaseModel):
    brand: str
    predicted_quantity_2026: float
    historical_growth_pct: float
    predicted_trend: str
    created_at: datetime

    class Config:
        from_attributes = True