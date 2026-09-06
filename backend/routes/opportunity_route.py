from fastapi import APIRouter, HTTPException
from backend.services import opportunity_service
from backend.schemas.opportunity_schema import OpportunitySchema
from typing import List

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/", response_model=List[OpportunitySchema])
async def list_opportunities():
    results = await opportunity_service.get_all_opportunities()
    if not results:
        raise HTTPException(404, "Aucune opportunité en base, lancez /pipeline/run.")
    return results