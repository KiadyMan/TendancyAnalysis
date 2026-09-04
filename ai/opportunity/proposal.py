import builtins
import pandas as pd

def calculate_opportunities(df_2026: pd.DataFrame) -> pd.DataFrame:
    """Ajoute le score d'opportunité et la proposition de produit."""
    max_val = df_2026['Predicted_Quantity_2026'].max()
    df_2026['OpportunityScore'] = df_2026['Predicted_Quantity_2026'].apply(
        lambda x: builtins.round((x / max_val) * 100, 0)
    )
    df_2026['ProposedProduct'] = df_2026['Brand'].apply(
        lambda brand: f"Écosystème Intelligent & Flagship {brand}"
    )
    return df_2026