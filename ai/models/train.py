import pickle
from sklearn.ensemble import RandomForestRegressor
from ai.preprocessing.features import load_and_preprocess_features
from ai.evaluation.evaluate import evaluate_predictions

def train_and_save_model(model_output_path: str = "ai/models/model.pkl"):
    """Entraîne le modèle Random Forest et sauvegarde l'artefact pkl."""
    df, df_monthly, X, y = load_and_preprocess_features()

    train_mask = df_monthly['Year'] <= 2024
    test_mask = df_monthly['Year'] == 2025

    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]

    model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    evaluate_predictions(y_test, y_pred)

    with open(model_output_path, "wb") as f:
        pickle.dump(model, f)

    print(f"Modèle sauvegardé avec succès dans : {model_output_path}")

if __name__ == "__main__":
    train_and_save_model()