from beanie import Document
from datetime import datetime
from pydantic import Field
from typing import Optional


class Opportunity(Document):
    brand: str
    predicted_quantity_2026: float
    opportunity_score: Optional[float] = None
    opportunity_label: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "opportunities"