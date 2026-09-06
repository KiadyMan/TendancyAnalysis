import subprocess
from ai.models.train import train_and_save_model
from ai.prediction.predict import run_predictions
from backend.models.trend import Trend
from backend.models.prediction import Prediction
from backend.models.opportunity import Opportunity
import pandas as pd

CLEANED_DATA_PATH = "data/processed/cleaned_data.csv"


def run_spark_job():
    """
    Spark tourne dans sa propre JVM — on l'exécute en subprocess
    plutôt que d'importer pyspark directement dans le process FastAPI
    (évite les conflits de mémoire/session Spark avec le serveur async).
    """
    result = subprocess.run(
        ["python", "-m", "data_processing.spark_job"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Échec du job Spark : {result.stderr}")


async def run_full_pipeline():
    """
    Enchaîne P1 → P3 → P4, puis pousse TOUT dans Mongo en un seul passage.
    C'est la tâche à lancer via BackgroundTasks depuis /pipeline/run.
    """
    # P1 : Spark nettoie et enrichit → écrit cleaned_data.csv
    run_spark_job()

    # P3 : entraîne le RandomForest → écrit model.pkl
    train_and_save_model()

    # P4 : projette 2026 + calcule les opportunités → un seul appel
    df_final = run_predictions()

    # --- Pousse les tendances (sortie de P1) ---
    df_trends = pd.read_csv(CLEANED_DATA_PATH, parse_dates=["SaleDate"])
    await Trend.delete_all()
    trend_docs = [
        Trend(
            product=row.get("Product"),
            brand=row["Brand"],
            price=row["Price"],
            sale_date=row["SaleDate"].date(),
            quantity=int(row["Quantity"]),
            region=row.get("Region"),
            ram=row.get("RAM"),
            rom=row.get("ROM"),
            revenue=row["Revenue"],
            prev_quantity=int(row["Prev_Quantity"]),
            growth_rate_pct=row["Growth_Rate_%"],
            trend=row["Trend"],
        )
        for _, row in df_trends.iterrows()
    ]
    if trend_docs:
        await Trend.insert_many(trend_docs)

    # --- Pousse les prédictions + opportunités (sortie de P4, un seul df_final) ---
    await Prediction.delete_all()
    await Opportunity.delete_all()

    prediction_docs = [
        Prediction(
            brand=row["Brand"],
            predicted_quantity_2026=row["Predicted_Quantity_2026"],
            historical_growth_pct=row["Historical_Growth_%"],
            predicted_trend=row["Predicted_Trend"],
        )
        for _, row in df_final.iterrows()
    ]
    opportunity_docs = [
        Opportunity(
            brand=row["Brand"],
            predicted_quantity_2026=row["Predicted_Quantity_2026"],
            opportunity_score=row.get("Opportunity_Score"),
            opportunity_label=row.get("Opportunity_Label"),
        )
        for _, row in df_final.iterrows()
    ]

    if prediction_docs:
        await Prediction.insert_many(prediction_docs)
    if opportunity_docs:
        await Opportunity.insert_many(opportunity_docs)

    return {
        "trends": len(trend_docs),
        "predictions": len(prediction_docs),
        "opportunities": len(opportunity_docs),
    }