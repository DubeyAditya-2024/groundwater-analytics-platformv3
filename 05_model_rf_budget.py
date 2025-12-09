import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import os

def train_rf_budget_model():
    # Define the directory path for saving the model
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_name = 'rf_water_budget.pkl'
    save_path = os.path.join(BASE_DIR, file_name)

    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("Error: 'prepared_data.csv' not found. Please run 01_data_pipeline.py first.")
        return

    # Define a simulated water budget/extraction target (Simulated for training purposes)
    df['Simulated_Extraction'] = (df['Water_Level'] * (df['Rainfall_mm'] - df['PET_mm']) / 10).clip(lower=0)

    # Features for Random Forest
    FEATURE_COLS = [
        'Water_Level', 'Rainfall_30days', 'PET_30days', 'Avg_Temp_C',
        'Elevation', 'Lat', 'Lon',
        'Soil_Type_Clay', 'Soil_Type_Loam', 'Soil_Type_Sand',
        'LULC_Agri', 'LULC_Forest', 'LULC_Urban'
    ]
    TARGET_COL = 'Simulated_Extraction'

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Split data
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train Random Forest Regressor
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)

    print("Training Random Forest Water Budget Model...")
    rf_model.fit(X_train, y_train)

    # Save the trained model using the absolute path
    try:
        joblib.dump(rf_model, save_path)
        print(f"✅ Random Forest Model saved successfully at: {save_path}")
    except Exception as e:
        print(f"CRITICAL FILE SAVE ERROR: Failed to save {file_name}. Error: {e}")

if __name__ == '__main__':
    train_rf_budget_model()