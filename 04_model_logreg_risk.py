import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os  # Added for path confirmation


def train_logreg_risk_model():
    try:
        df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("Error: 'prepared_data.csv' not found. Please run 01_data_pipeline.py first.")
        return

    # --- Data Definition and Transformation ---

    # Check if Target_Recharge column exists before proceeding
    if 'Target_Recharge' not in df.columns:
        print("CRITICAL ERROR: 'Target_Recharge' column is missing. Did 01_data_pipeline.py run correctly?")
        return

    # Define a risk threshold: Use the 20th percentile of the target data as a threshold for a "critical drop".
    RISK_THRESHOLD = df['Target_Recharge'].quantile(0.20)

    # Create the binary target variable (1 = High Risk, 0 = Low Risk)
    df['Risk_Target'] = (df['Target_Recharge'] < RISK_THRESHOLD).astype(int)

    # Features for risk model
    FEATURE_COLS = ['Water_Level', 'Rainfall_30days', 'PET_30days', 'Target_Recharge']
    TARGET_COL = 'Risk_Target'

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # --- Training ---

    # Split and Scale Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Initialize and train Logistic Regression model
    logreg_model = LogisticRegression(solver='liblinear', random_state=42)

    print("Training Logistic Regression Drought Risk Model...")
    logreg_model.fit(X_train_scaled, y_train)

    # --- Saving with Absolute Path Confirmation ---

    risk_file = 'logistic_risk_index.pkl'
    scaler_file = 'risk_scaler.pkl'

    try:
        joblib.dump(logreg_model, risk_file)
        joblib.dump(scaler, scaler_file)

        print(f"✅ Logistic Regression Model saved successfully at: {os.path.abspath(risk_file)}")
        print(f"✅ Risk Scaler saved successfully at: {os.path.abspath(scaler_file)}")

    except Exception as e:
        print(f"CRITICAL FILE SAVE ERROR: Failed to save files. Error: {e}")


if __name__ == '__main__':
    train_logreg_risk_model()