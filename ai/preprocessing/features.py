import pandas as pd

def load_and_preprocess_features(data_path: str = "data/processed/cleaned_data.csv"):
    """Charge les données et prépare les variables agrégées pour le ML."""
    df = pd.read_csv(data_path)
    df['SaleDate'] = pd.to_datetime(df['SaleDate'])
    df['Year'] = df['SaleDate'].dt.year
    df['Month'] = df['SaleDate'].dt.month

    # Agrégation mensuelle par marque
    df_monthly = df.groupby(['Brand', 'Year', 'Month']).agg(
        Monthly_Qty=('Quantity', 'sum'),
        Avg_Price=('Price', 'mean'),
        Tx_Count=('Quantity', 'count')
    ).reset_index()

    # Feature Encoding
    X = pd.get_dummies(df_monthly[['Brand', 'Month', 'Avg_Price', 'Tx_Count']], drop_first=True)
    y = df_monthly['Monthly_Qty']
    
    return df, df_monthly, X, y