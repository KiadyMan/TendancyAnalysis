from beanie import Document
from datetime import datetime
from pydantic import Field


class Prediction(Document):
    brand: str
    predicted_quantity_2026: float
    historical_growth_pct: float
    predicted_trend: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "predictions"