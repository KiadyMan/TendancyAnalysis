from fastapi import APIRouter, HTTPException
from backend.services import prediction_service
from backend.schemas.prediction_schema import PredictionSchema
from typing import List

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/", response_model=List[PredictionSchema])
async def list_predictions():
    results = await prediction_service.get_all_predictions()
    if not results:
        raise HTTPException(404, "Aucune prédiction en base, lancez /pipeline/run.")
    return results


@router.get("/{brand}", response_model=List[PredictionSchema])
async def get_brand_prediction(brand: str):
    results = await prediction_service.get_predictions_by_brand(brand)
    if not results:
        raise HTTPException(404, f"Marque '{brand}' introuvable.")
    return results