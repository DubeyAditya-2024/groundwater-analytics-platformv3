import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor


def train_xgb_recharge_model():
    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("Error: 'prepared_data.csv' not found. Please run 01_data_pipeline.py first.")
        return

    # Features for XGBoost (uses processed data, including engineered features)
    FEATURE_COLS = [
        'Water_Level', 'Rainfall_30days', 'PET_30days', 'Avg_Temp_C',
        'Elevation', 'Lat', 'Lon',
        'Soil_Type_Clay', 'Soil_Type_Loam', 'Soil_Type_Sand',
        'LULC_Agri', 'LULC_Forest', 'LULC_Urban'
    ]
    TARGET_COL = 'Target_Recharge'  # The net level change over 30 days

    # Prepare data
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Initialize and train XGBoost Regressor
    xgb_model = XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        objective='reg:squarederror',
        random_state=42
    )

    print("Training XGBoost Recharge Model...")
    xgb_model.fit(X, y)

    # Save the trained model
    file_name = 'xgb_recharge_estimator.pkl'
    joblib.dump(xgb_model, file_name)

    print(f"✅ XGBoost Recharge Model trained and saved successfully as {file_name}")


if __name__ == '__main__':
    train_xgb_recharge_model()