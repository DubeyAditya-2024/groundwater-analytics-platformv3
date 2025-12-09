import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
import os


def train_if_anomaly_model():
    # Define the directory path for saving the model
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_name = 'if_anomaly_detector.pkl'
    save_path = os.path.join(BASE_DIR, file_name)

    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("Error: 'prepared_data.csv' not found. Please run 01_data_pipeline.py first.")
        return

    # Features for Anomaly Detection
    FEATURE_COLS = ['Water_Level', 'Rainfall_mm', 'PET_mm', 'Avg_Temp_C', 'Prev_Level']

    # Prepare data
    X = df[FEATURE_COLS].copy()  # Use .copy() to avoid SettingWithCopyWarning

    # Simple feature engineering for Isolation Forest (e.g., rate of change)
    X['Level_Change_Rate'] = X['Water_Level'].diff().fillna(0)

    # Use key features for fitting the model
    if_features = X[['Water_Level', 'Level_Change_Rate', 'Rainfall_mm']]

    # Initialize and train Isolation Forest model
    if_model = IsolationForest(contamination=0.01, random_state=42, n_jobs=-1)

    print("Training Isolation Forest Anomaly Detector...")
    if_model.fit(if_features)

    # Save the trained model using the absolute path
    try:
        joblib.dump(if_model, save_path)
        print(f"✅ Isolation Forest Model saved successfully at: {save_path}")
    except Exception as e:
        print(f"CRITICAL FILE SAVE ERROR: Failed to save {file_name}. Error: {e}")


if __name__ == '__main__':
    train_if_anomaly_model()