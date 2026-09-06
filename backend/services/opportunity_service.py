from ai.prediction.predict import run_predictions
from backend.models.opportunity import Opportunity


async def refresh_opportunities():
    """
    run_predictions() appelle déjà calculate_opportunities() en interne
    et retourne un DataFrame enrichi (df_final). On réutilise ce même
    appel plutôt que de dupliquer la logique.
    """
    df_final = run_predictions()

    await Opportunity.delete_all()

    docs = [
        Opportunity(
            brand=row["Brand"],
            predicted_quantity_2026=row["Predicted_Quantity_2026"],
            opportunity_score=row.get("Opportunity_Score"),
            opportunity_label=row.get("Opportunity_Label"),
        )
        for _, row in df_final.iterrows()
    ]
    if docs:
        await Opportunity.insert_many(docs)

    return len(docs)


async def get_all_opportunities():
    return await Opportunity.find_all().to_list()