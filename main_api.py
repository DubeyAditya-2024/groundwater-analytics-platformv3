from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pandas as pd
from contextlib import asynccontextmanager
import os
import time
import math

# --- 1. Define Static Station Configuration (Simulating a Database) ---
# This data would typically come from a persistent database lookup.
STATION_CONFIG = {
    "Station_001_AgriLoam": {
        "lat": 23.0, "lon": 77.0, "elevation": 300.0,
        "soil_type": "Loam", "lulc": "Agri"
    },
    "Station_002_ForestSand": {
        "lat": 25.5, "lon": 78.5, "elevation": 450.0,
        "soil_type": "Sand", "lulc": "Forest"
    },
    "Station_003_UrbanClay": {
        "lat": 28.0, "lon": 77.2, "elevation": 250.0,
        "soil_type": "Clay", "lulc": "Urban"
    }
}

# Lookup table for typical Specific Yield (Sy) values based on soil type
SPECIFIC_YIELD_LOOKUP = {
    "Loam": 0.18,
    "Sand": 0.25,
    "Clay": 0.05
}


# --- 2. Define the Input Data Structure (Pydantic Model) ---
class StationInput(BaseModel):
    station_id: str = Field(..., description="Unique identifier for the monitoring station.")


# --- 3. Mock Function to Simulate Real-Time DWLR and Official Weather Data ---
def get_real_time_data(station_id, lat, lon):
    """
    Simulates real-time data fetch from DWLR Cloud and Official Weather API.
    Uses current time to ensure values change on every API call (for 'real-time' demo).
    """

    # Use current time in hours for cyclical change
    current_time_hr = (time.time() / 3600) % 24

    # Generate based on a sinusoidal function for realistic, continuous change
    # Water Level (Simulated DWLR) - Cycles between 14.0m and 16.0m
    water_level = 15.0 + 1.0 * math.sin(current_time_hr / 4)

    # Rainfall (Simulated Official Weather API) - Higher during certain 'hours'
    rainfall_mm = 5.0 + 3.0 * math.cos(current_time_hr / 12)
    rainfall_mm = max(0.0, rainfall_mm)  # Cannot be negative

    # Temperature (Simulated Official Weather API) - Cycles between 20C and 30C
    avg_temp_c = 25.0 + 5.0 * math.sin(current_time_hr / 8)

    # Potential Evapotranspiration (Simulated Official API) - Depends on Temp/Solar
    pet_mm = 3.5 + 1.5 * math.sin(current_time_hr / 10)

    # Add minor station-specific bias
    bias = STATION_CONFIG[station_id]['elevation'] / 1000.0
    water_level -= bias * 0.5

    return {
        "water_level": float(f"{water_level:.2f}"),
        "rainfall_mm": float(f"{rainfall_mm:.2f}"),
        "avg_temp_c": float(f"{avg_temp_c:.2f}"),
        "pet_mm": float(f"{pet_mm:.2f}")
    }


# --- 4. Application Lifespan & Model Loading ---

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def get_model_path(filename):
        return os.path.join(BASE_DIR, filename)

    try:
        # Note: 'lstm_water_level_predictor.keras' is used instead of '.h5'
        models["lstm"] = load_model(get_model_path("lstm_water_level_predictor.keras"))
        models["xgb"] = joblib.load(get_model_path("xgb_recharge_estimator.pkl"))
        models["logreg"] = joblib.load(get_model_path("logistic_risk_index.pkl"))
        models["rf"] = joblib.load(get_model_path("rf_water_budget.pkl"))
        models["iforest"] = joblib.load(get_model_path("if_anomaly_detector.pkl"))
        models["lstm_scaler"] = joblib.load(get_model_path("lstm_scaler.pkl"))
        models["risk_scaler"] = joblib.load(get_model_path("risk_scaler.pkl"))
        models["ohe"] = joblib.load(get_model_path("ohe_encoder.pkl"))

        print("All models and scalers loaded successfully.")
    except Exception as e:
        # This will now correctly load the files you provided
        print(f"Error loading models: {e}")
        raise HTTPException(status_code=500,
                            detail="Model loading failed. Ensure all 8 required model/scaler/encoder files are in the same directory.")
    yield
    models.clear()


app = FastAPI(
    title="Groundwater Predictive Analytics API",
    version="1.0",
    description="Five-in-One Model Suite for Smart Water Management",
    lifespan=lifespan
)


# --- 5. Prediction Endpoint (Updated for Station ID) ---

@app.post("/predict_all")
def predict_all(data: StationInput):
    # 1. Lookup Static Configuration
    station_id = data.station_id
    if station_id not in STATION_CONFIG:
        raise HTTPException(status_code=404, detail=f"Station ID '{station_id}' not found.")

    static_data = STATION_CONFIG[station_id]

    # 2. Fetch Dynamic Real-Time Data (Simulating DWLR/Weather API calls)
    real_time_data = get_real_time_data(station_id, static_data['lat'], static_data['lon'])

    # 3. Combine Static and Dynamic Data into a single dictionary
    combined_data = {**static_data, **real_time_data}

    # 4. Create DataFrame and Proceed with Preprocessing
    input_df = pd.DataFrame([combined_data])

    # CRITICAL RENAME: Rename inputs to match the CAPITALIZATION expected by models
    input_df.rename(columns={
        'water_level': 'Water_Level',
        'rainfall_mm': 'Rainfall_mm',
        'avg_temp_c': 'Avg_Temp_C',
        'pet_mm': 'PET_mm',
        'lat': 'Lat',
        'lon': 'Lon',
        'elevation': 'Elevation'
    }, inplace=True)

    # One-Hot Encoding for categorical features (Soil, LULC)
    ohe_input_df = input_df[['soil_type', 'lulc']].rename(columns={
        'soil_type': 'Soil_Type',
        'lulc': 'LULC'
    })

    ohe_features = models["ohe"].transform(ohe_input_df)
    ohe_df = pd.DataFrame(ohe_features, columns=models["ohe"].get_feature_names_out(['Soil_Type', 'LULC']))
    input_df = pd.concat([input_df.reset_index(drop=True), ohe_df], axis=1)

    # Add placeholder/historical and derived features
    input_df['Prev_Level'] = input_df['Water_Level']
    input_df['Rainfall_7day'] = input_df['Rainfall_mm'] * 7
    input_df['Rainfall_30days'] = input_df['Rainfall_mm'] * 30
    input_df['PET_30days'] = input_df['PET_mm'] * 30

    # Correction: Add Level_Change_Rate feature for Isolation Forest model
    # Since this is a single real-time reading, we assume a zero change rate,
    # which is consistent with the model training script's handling of the first observation.
    input_df['Level_Change_Rate'] = 0.0

    # --- 5.1. Run Predictions ---
    results = {}

    # 1. Anomaly Detection (Isolation Forest)
    # Corrected Feature selection: uses 'Level_Change_Rate' as required by the model
    if_features = input_df[['Water_Level', 'Level_Change_Rate', 'Rainfall_mm']]
    anomaly_score = models["iforest"].decision_function(if_features)[0]
    # NOTE: The threshold (-0.1) is a common, empirical starting point for anomaly detection.
    is_anomaly = "Yes" if anomaly_score < -0.1 else "No"
    results["Anomaly_Check"] = {"Is_Anomaly": is_anomaly, "Score": float(f"{anomaly_score:.4f}")}

    # 2. LSTM Water Fluctuation (Next Day Level)
    lstm_features = input_df[['Water_Level', 'Rainfall_7day', 'PET_mm', 'Avg_Temp_C', 'Prev_Level']].values
    lstm_scaled = models["lstm_scaler"].transform(lstm_features).reshape(1, 1, len(lstm_features[0]))
    next_day_level = models["lstm"].predict(lstm_scaled, verbose=0)[0][0]
    results["Water_Level_Prediction"] = {"Next_Day_Level": float(f"{next_day_level:.2f}")}

    # 3. XGBoost Recharge Estimation (30-day net change)
    xgb_cols = [c for c in models["xgb"].feature_names_in_ if c in input_df.columns]
    xgb_input = input_df[xgb_cols]
    estimated_recharge = models["xgb"].predict(xgb_input)[0]
    results["Estimated_Recharge"] = {"30_Day_Net_Change": float(f"{estimated_recharge:.2f}")}

    # 4. Random Forest Water Budget (Simulated Extraction)
    rf_cols = [c for c in models["rf"].feature_names_in_ if c in input_df.columns]
    rf_input = input_df[rf_cols]
    simulated_extraction = models["rf"].predict(rf_input)[0]
    results["Simulated_Extraction"] = {"Rate": float(f"{simulated_extraction:.2f}")}

    # 5. Logistic Regression Risk Index
    risk_features = input_df[['Water_Level', 'Rainfall_30days', 'PET_30days']].copy()
    risk_features['Target_Recharge'] = estimated_recharge
    risk_input = models["risk_scaler"].transform(risk_features.values)
    risk_proba = models["logreg"].predict_proba(risk_input)[0][1]
    results["Drought_Risk_Index"] = {"Probability_Critical_Drop": float(f"{risk_proba:.2f}")}

    # --- 5.2. NEW FEATURE: Aquifer Volume Calculation (Artificial Recharge Potential) ---
    current_level = input_df['Water_Level'].iloc[0]
    next_day_level = results["Water_Level_Prediction"]["Next_Day_Level"]

    # Calculate change in head (Δh): Positive means rise (Recharge)
    Ah = next_day_level - current_level

    # Look up Specific Yield (Sy) based on the station's soil type
    Sy = SPECIFIC_YIELD_LOOKUP.get(static_data['soil_type'], 0.15)

    # Assume a standard monitoring area (A) of 1 km² = 1,000,000 m² for demonstration.
    A_sq_m = 1000000.0

    # Volume = Sy * A * Δh (Output in cubic meters, m³)
    volume_change_m3 = Sy * A_sq_m * Ah

    results["Aquifer_Volume_Change"] = {
        "volume_change_m3": float(f"{volume_change_m3:.2f}"),
        "process": "Potential Recharge" if volume_change_m3 >= 0 else "Potential Net Drain",
        "Sy_Used": Sy,
        "A_Used_sq_m": A_sq_m
    }
    # ---------------------------------------------------------------------------------

    # 6. Add real-time input data to the response for display in the dashboard
    results["Real_Time_Input"] = combined_data

    return results