from ai.prediction.predict import run_predictions
from backend.models.prediction import Prediction


async def refresh_predictions():
    """Relance P4 (run_predictions) et pousse le résultat dans Mongo."""
    df_final = run_predictions()  # exécute P4 en synchrone (pandas/sklearn)

    await Prediction.delete_all()

    docs = [
        Prediction(
            brand=row["Brand"],
            predicted_quantity_2026=row["Predicted_Quantity_2026"],
            historical_growth_pct=row["Historical_Growth_%"],
            predicted_trend=row["Predicted_Trend"],
        )
        for _, row in df_final.iterrows()
    ]
    if docs:
        await Prediction.insert_many(docs)

    return len(docs)


async def get_all_predictions():
    return await Prediction.find_all().to_list()


async def get_predictions_by_brand(brand: str):
    return await Prediction.find(
        Prediction.brand == brand
    ).to_list()