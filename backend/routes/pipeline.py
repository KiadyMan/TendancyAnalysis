from fastapi import APIRouter, BackgroundTasks
from backend.services.pipeline_service import run_full_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
async def run_pipeline(background_tasks: BackgroundTasks):
    """
    Déclenche P1 (Spark) → P3 (entraînement) → P4 (prédictions)
    puis pousse tout dans MongoDB. Tourne en arrière-plan car
    Spark + entraînement peuvent prendre plusieurs minutes.
    """
    background_tasks.add_task(run_full_pipeline)
    return {
        "status": "started",
        "message": "Pipeline P1→P4 lancé en arrière-plan. Consultez les logs serveur pour le suivi."
    }