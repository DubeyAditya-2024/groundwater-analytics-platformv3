import pandas as pd
import numpy as np
import joblib
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, f1_score
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model


# --- Helper Functions for Metric Calculation ---

def calculate_rmse(y_true, y_pred, model_name):
    """Calculates and prints the Root Mean Squared Error."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"✅ {model_name} RMSE: {rmse:.4f}")


def calculate_f1(y_true, y_pred, model_name):
    """Calculates and prints the F1 Score."""
    f1 = f1_score(y_true, y_pred)
    print(f"✅ {model_name} F1 Score: {f1:.4f}")


# --- 1. Evaluate LSTM Water Level Prediction (Regression) ---

def evaluate_lstm_model():
    print("--- Evaluating LSTM Water Level Model ---")
    try:
        # Load Data
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
        # Load Model and Scaler
        # Uses 'lstm_water_level_predictor.keras' as confirmed by file list
        model = load_model('lstm_water_level_predictor.keras')
        # Uses 'lstm_scaler.pkl' as confirmed by file list
        scaler = joblib.load('lstm_scaler.pkl')
    except FileNotFoundError as e:
        print(f"Error: Required file not found. Ensure all preceding scripts were run. ({e})")
        return

    FEATURES = ['Water_Level', 'Rainfall_7day', 'PET_mm', 'Avg_Temp_C', 'Prev_Level']
    SEQ_LENGTH = 30

    # Replicate Scaling
    df_scaled = pd.DataFrame(scaler.transform(df[FEATURES]), columns=FEATURES, index=df.index)

    # Replicate Sequence Creation
    X, y = [], []
    for i in range(len(df_scaled) - SEQ_LENGTH):
        X.append(df_scaled.iloc[i:(i + SEQ_LENGTH)][FEATURES].values)
        y.append(df['Water_Level'].iloc[i + SEQ_LENGTH])

    X, y = np.array(X), np.array(y)

    # Replicate Test/Train Split (90% train, 10% test)
    split_point = int(0.9 * len(X))
    X_test, y_test = X[split_point:], y[split_point:]

    # Reshape X_test to match the model's expected shape (None, 1, 5)
    X_test_reshaped = X_test[:, -1:, :]

    # Predict
    y_pred_scaled = model.predict(X_test_reshaped, verbose=0)

    # Inverse Transform the predictions
    dummy_array = np.zeros((len(y_pred_scaled), len(FEATURES)))
    dummy_array[:, 0] = y_pred_scaled.flatten()
    y_pred_original = scaler.inverse_transform(dummy_array)[:, 0]

    # Evaluate (y_test is already on the original scale)
    calculate_rmse(y_test, y_pred_original, "LSTM Water Level")


# --- 2. Evaluate XGBoost Recharge Prediction (Regression) ---

def evaluate_xgb_model():
    print("\n--- Evaluating XGBoost Recharge Model ---")
    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
        # FIX: Changed filename to match user's file list: 'xgb_recharge_estimator.pkl'
        model = joblib.load('xgb_recharge_estimator.pkl')
    except FileNotFoundError as e:
        print(f"Error: Required file not found. Ensure all preceding scripts were run. ({e})")
        return

    FEATURE_COLS = [
        'Water_Level', 'Rainfall_30days', 'PET_30days', 'Avg_Temp_C',
        'Elevation', 'Lat', 'Lon',
        'Soil_Type_Clay', 'Soil_Type_Loam', 'Soil_Type_Sand',
        'LULC_Agri', 'LULC_Forest', 'LULC_Urban'
    ]
    TARGET_COL = 'Target_Recharge'

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Replicate Test/Train Split (assuming 80/20, common standard)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Predict
    y_pred = model.predict(X_test)

    # Evaluate
    calculate_rmse(y_test, y_pred, "XGBoost Recharge")


# --- 3. Evaluate Logistic Regression Drought Risk (Classification) ---

def evaluate_logreg_model():
    print("\n--- Evaluating Logistic Regression Risk Model ---")
    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
        # Uses 'logistic_risk_index.pkl' and 'risk_scaler.pkl' as confirmed by file list
        model = joblib.load('logistic_risk_index.pkl')
        scaler = joblib.load('risk_scaler.pkl')
    except FileNotFoundError as e:
        print(f"Error: Required file not found. Ensure all preceding scripts were run. ({e})")
        return

    # Replicate Target Creation (from 04_model_logreg_risk.py)
    RISK_THRESHOLD = df['Target_Recharge'].quantile(0.20)
    df['Risk_Target'] = (df['Target_Recharge'] < RISK_THRESHOLD).astype(int)

    FEATURE_COLS = ['Water_Level', 'Rainfall_30days', 'PET_30days', 'Target_Recharge']
    TARGET_COL = 'Risk_Target'

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Replicate Test/Train Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the Test Data (required for LogReg model trained on scaled data)
    X_test_scaled = scaler.transform(X_test)

    # Predict
    y_pred = model.predict(X_test_scaled)

    # Evaluate
    calculate_f1(y_test, y_pred, "Logistic Regression Risk")


# --- 4. Evaluate Random Forest Budget Prediction (Regression) ---

def evaluate_rf_model():
    print("\n--- Evaluating Random Forest Budget Model ---")
    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
        # Uses 'rf_water_budget.pkl' as confirmed by file list
        model = joblib.load('rf_water_budget.pkl')
    except FileNotFoundError as e:
        print(f"Error: Required file not found. Ensure all preceding scripts were run. ({e})")
        return

    # Replicate Target Creation (from 05_model_rf_budget.py)
    if 'Rainfall_mm' not in df.columns or 'PET_mm' not in df.columns:
        print("Error: Rainfall_mm or PET_mm missing for target calculation.")
        return

    df['Simulated_Extraction'] = (df['Water_Level'] * (df['Rainfall_mm'] - df['PET_mm']) / 10).clip(lower=0)

    FEATURE_COLS = [
        'Water_Level', 'Rainfall_30days', 'PET_30days', 'Avg_Temp_C',
        'Elevation', 'Lat', 'Lon',
        'Soil_Type_Clay', 'Soil_Type_Loam', 'Soil_Type_Sand',
        'LULC_Agri', 'LULC_Forest', 'LULC_Urban'
    ]
    TARGET_COL = 'Simulated_Extraction'

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Replicate Test/Train Split (assuming 80/20, common standard)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Predict
    y_pred = model.predict(X_test)

    # Evaluate
    calculate_rmse(y_test, y_pred, "Random Forest Budget")


if __name__ == '__main__':
    # Ensure TensorFlow is not using GPU for these simple predictions, preventing issues
    tf.config.set_visible_devices([], 'GPU')
    print("Starting Model Evaluation...")

    if not os.path.exists('prepared_data.csv'):
        print("\nCRITICAL: 'prepared_data.csv' not found. Please run '01_data_pipeline.py' first.")
    else:
        evaluate_lstm_model()
        evaluate_xgb_model()
        evaluate_logreg_model()
        evaluate_rf_model()

    print("\nEvaluation complete.")