from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OpportunitySchema(BaseModel):
    brand: str
    predicted_quantity_2026: float
    opportunity_score: Optional[float] = None
    opportunity_label: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True