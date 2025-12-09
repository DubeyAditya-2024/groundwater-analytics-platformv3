import joblib
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
import math
import os
from main_api import STATION_CONFIG, SPECIFIC_YIELD_LOOKUP, get_real_time_data  # Import necessary constants/functions

# --- Configuration ---
TEST_STATION_ID = "Station_001_AgriLoam"  # Change this to test other stations


# ---------------------

def load_all_models():
    """Loads all models necessary for the full prediction pipeline."""
    models = {}
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def get_model_path(filename):
        return os.path.join(BASE_DIR, filename)

    try:
        # Load all models as in main_api.py's lifespan function
        models["lstm"] = load_model(get_model_path("lstm_water_level_predictor.keras"))
        models["xgb"] = joblib.load(get_model_path("xgb_recharge_estimator.pkl"))
        models["logreg"] = joblib.load(get_model_path("logistic_risk_index.pkl"))
        models["rf"] = joblib.load(get_model_path("rf_water_budget.pkl"))
        models["iforest"] = joblib.load(get_model_path("if_anomaly_detector.pkl"))
        models["lstm_scaler"] = joblib.load(get_model_path("lstm_scaler.pkl"))
        models["risk_scaler"] = joblib.load(get_model_path("risk_scaler.pkl"))
        models["ohe"] = joblib.load(get_model_path("ohe_encoder.pkl"))
        print("✅ All required models loaded successfully.")
        return models
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print("Please ensure you have run all model training scripts (01_data_pipeline.py through 06_model_*.py).")
        return None


def calculate_recharge_potential(station_id, models):
    """Replicates the core prediction logic from main_api.py/predict_all."""

    if station_id not in STATION_CONFIG:
        print(f"Error: Station ID '{station_id}' not found.")
        return

    static_data = STATION_CONFIG[station_id]
    real_time_data = get_real_time_data(station_id, static_data['lat'], static_data['lon'])
    combined_data = {**static_data, **real_time_data}
    input_df = pd.DataFrame([combined_data])

    # 1. Preprocessing (Identical to main_api.py)
    input_df.rename(columns={
        'water_level': 'Water_Level', 'rainfall_mm': 'Rainfall_mm',
        'avg_temp_c': 'Avg_Temp_C', 'pet_mm': 'PET_mm',
        'lat': 'Lat', 'lon': 'Lon', 'elevation': 'Elevation'
    }, inplace=True)
    ohe_input_df = input_df[['soil_type', 'lulc']].rename(columns={'soil_type': 'Soil_Type', 'lulc': 'LULC'})
    ohe_features = models["ohe"].transform(ohe_input_df)
    ohe_df = pd.DataFrame(ohe_features, columns=models["ohe"].get_feature_names_out(['Soil_Type', 'LULC']))
    input_df = pd.concat([input_df.reset_index(drop=True), ohe_df], axis=1)
    input_df['Prev_Level'] = input_df['Water_Level']
    input_df['Rainfall_7day'] = input_df['Rainfall_mm'] * 7
    input_df['PET_mm'] = input_df['PET_mm']  # Ensure PET_mm is still available for LSTM

    # 2. Run LSTM Water Fluctuation Prediction
    # This prediction is CRITICAL for the Artificial Recharge Calculation (Step 3)
    lstm_features = input_df[['Water_Level', 'Rainfall_7day', 'PET_mm', 'Avg_Temp_C', 'Prev_Level']].values
    lstm_scaled = models["lstm_scaler"].transform(lstm_features).reshape(1, 1, len(lstm_features[0]))
    next_day_level = models["lstm"].predict(lstm_scaled, verbose=0)[0][0]

    # 3. Aquifer Volume Calculation (Artificial Recharge Potential)
    current_level = input_df['Water_Level'].iloc[0]
    Ah = next_day_level - current_level  # Change in head (Δh)
    Sy = SPECIFIC_YIELD_LOOKUP.get(static_data['soil_type'], 0.15)
    A_sq_m = 1000000.0  # 1 km² area assumption

    volume_change_m3 = Sy * A_sq_m * Ah

    print("\n=======================================================")
    print(f"Station: {station_id}")
    print(f"Real-Time Water Level: {current_level:.2f}m")
    print(f"Predicted Next Day Level (LSTM): {next_day_level:.2f}m")
    print(f"Change in Water Head (\u0394h): {Ah:.2f}m")
    print(f"Specific Yield (Sy) Used: {Sy}")
    print("-------------------------------------------------------")
    print(f"Artificial Recharge Potential (Volume Change):")
    print(f"{volume_change_m3:,.2f} m\u00B3")
    print(f"Process: {'Potential Recharge' if volume_change_m3 >= 0 else 'Potential Net Drain'}")
    print("=======================================================")


if __name__ == '__main__':
    # Ensure TensorFlow is not using eager execution for clean script runs
    tf.config.run_functions_eagerly(False)

    loaded_models = load_all_models()
    if loaded_models:
        calculate_recharge_potential(TEST_STATION_ID, loaded_models)