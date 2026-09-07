import builtins
import pickle
import pandas as pd
from ai.preprocessing.features import load_and_preprocess_features
from ai.opportunity.proposal import calculate_opportunities

def run_predictions(
    model_path: str = "ai/models/model.pkl",
    output_path: str = "data/processed/p2_predictions_output.csv"
):
    """Charge le modèle pkl, effectue les projections 2026 via model.predict() et sauvegarde le CSV."""
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    df, df_monthly, X, y = load_and_preprocess_features()
    df_2026_list = []

    for brand in df['Brand'].unique():
        b_2025 = df_monthly[(df_monthly['Brand'] == brand) & (df_monthly['Year'] == 2025)]
        b_2024 = df_monthly[(df_monthly['Brand'] == brand) & (df_monthly['Year'] == 2024)]

        if b_2025.empty:
            continue 
        
        qty_2025 = b_2025['Monthly_Qty'].sum()
        qty_2024 = b_2024['Monthly_Qty'].sum()
        growth_rate = ((qty_2025 - qty_2024) / qty_2024) if qty_2024 > 0 else 0.0

        # Construit une ligne de features par mois pour 2026,
        # en utilisant les moyennes 2025 comme proxy (Avg_Price, Tx_Count)
        avg_price_2025 = b_2025['Avg_Price'].mean()
        avg_tx_2025 = b_2025['Tx_Count'].mean()

        monthly_preds = []
        for month in range(1, 13):
            row_features = pd.DataFrame([{
                "Brand": brand,
                "Month": month,
                "Avg_Price": avg_price_2025,
                "Tx_Count": avg_tx_2025,
            }])
            row_encoded = pd.get_dummies(row_features, drop_first=True)
            # Aligne les colonnes avec celles vues à l'entraînement (X)
            row_encoded = row_encoded.reindex(columns=X.columns, fill_value=0)
            monthly_pred = model.predict(row_encoded)[0]
            monthly_preds.append(monthly_pred)

        pred_2026_qty = sum(monthly_preds)
        trend = "Forte Hausse" if growth_rate > 0.05 else ("Baisse" if growth_rate < -0.05 else "Stable")
 
        df_2026_list.append({
            "Brand": brand,
            "Predicted_Quantity_2026": builtins.round(pred_2026_qty, 0),
            "Historical_Growth_%": builtins.round(growth_rate * 100, 2),
            "Predicted_Trend": trend
        })

    df_2026 = pd.DataFrame(df_2026_list).sort_values(by="Predicted_Quantity_2026", ascending=False)
    df_final = calculate_opportunities(df_2026)

    df_final.to_csv(output_path, index=False)
    print(f"Prédictions 2026 générées et sauvegardées dans : {output_path}")
    return df_final

if __name__ == "__main__":
    run_predictions()