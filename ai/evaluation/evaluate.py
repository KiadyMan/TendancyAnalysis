import builtins
from sklearn.metrics import r2_score, mean_absolute_error

def evaluate_predictions(y_true, y_pred) -> dict:
    """Calcule et affiche les métriques R2 et MAE."""
    r2 = r2_score(y_true, y_pred) * 100
    mae = mean_absolute_error(y_true, y_pred)
    
    print("=== ÉVALUATION DU MODÈLE ===")
    print(f"Précision R² : {builtins.round(r2, 2)}%")
    print(f"Erreur MAE   : {builtins.round(mae, 2)} unités/mois")
    
    return {"r2": r2, "mae": mae}