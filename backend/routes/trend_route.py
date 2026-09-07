from fastapi import APIRouter, HTTPException, Query
from backend.services import trend_service
from backend.schemas.trend_schema import TrendSchema
from typing import List, Optional

router = APIRouter(prefix="/trends", tags=["trends"])

# endpoint pour voir l'historique des ventes de chaque produit avec leur trends s'ils sont Hausse,Faible,Baisse
@router.get("/", response_model=List[TrendSchema])
async def list_trends(limit: int = Query(100, le=5000)):
    results = await trend_service.get_all_trends(limit=limit)
    if not results:
        raise HTTPException(404, "Aucune donnée de tendance en base.")
    return results


@router.get("/{brand}", response_model=List[TrendSchema])
async def get_brand_trends(brand: str, limit: int = Query(100, le=5000)):
    results = await trend_service.get_trends_by_brand(brand, limit=limit)
    if not results:
        raise HTTPException(404, f"Aucune donnée pour la marque '{brand}'.")
    return results