import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import OneHotEncoder
import joblib
from collections import Counter

def create_simulated_data(num_samples=1000):
    """Generates synthetic data for testing if real data is unavailable."""
    dates = pd.date_range(start='2020-01-01', periods=num_samples, freq='D')

    # Create simulated data structure matching expected real data after cleaning
    df = pd.DataFrame({
        'Date': dates,
        'Water_Level': np.random.rand(num_samples) * 20 + 50,
        'Rainfall_mm': np.random.rand(num_samples) * 10,
        'PET_mm': np.random.rand(num_samples) * 5,
        'Avg_Temp_C': np.random.rand(num_samples) * 15 + 20,
        'Lat': np.random.choice([10.0, 10.1, 10.2], num_samples),
        'Lon': np.random.choice([78.0, 78.1, 78.2], num_samples),
        'Elevation': np.random.choice([200, 250, 300], num_samples),
        'Soil_Type': np.random.choice(['Clay', 'Sand', 'Loam'], num_samples),
        'LULC': np.random.choice(['Agri', 'Urban', 'Forest'], num_samples)
    })

    print("⚠️ Using simulated data as a fallback. Fix raw_data.csv to use real data.")
    return df.set_index('Date').sort_index()


def load_real_data(csv_path="raw_data.csv"):
    """Attempts to load and clean the real data from the CSV file."""
    print(f"Attempting to load real data from: {os.path.abspath(csv_path)}")
    try:
        # Load the file
        df_raw = pd.read_csv(csv_path, encoding='utf-8', sep=',')

        # *** ROBUST COLUMN CLEANUP ***
        # 1. Strip whitespace from all column names.
        # 2. Remove the parenthesis (which caused the 'WATER LEVEL (' issue).
        df_raw.columns = df_raw.columns.str.strip().str.replace('(', '', regex=False).str.replace(')', '', regex=False)

        # Standardize column names
        df_raw.rename(columns={
            'TIMESTAMP': 'Date',
            'WATER LEVEL': 'Water_Level',
            'LATITUDE': 'Lat',
            'LONGITUDE': 'Lon'
        }, inplace=True)

        # Select key columns and add placeholders for environmental data not in the CSV
        df = df_raw[['Date', 'Water_Level', 'Lat', 'Lon']].copy()

        # --- Add placeholder environmental/static features (required for models) ---
        # NOTE: If you have a separate file with Rainfall, PET, and Temperature, you must integrate it here.
        df['Rainfall_mm'] = np.random.rand(len(df)) * 10
        df['PET_mm'] = np.random.rand(len(df)) * 5
        df['Avg_Temp_C'] = np.random.rand(len(df)) * 15 + 20
        df['Elevation'] = 250.0
        df['Soil_Type'] = np.random.choice(['Clay', 'Sand', 'Loam'], len(df))
        df['LULC'] = np.random.choice(['Agri', 'Urban', 'Forest'], len(df))

        # Final cleaning steps
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Handle the non-unique index issue by keeping only the last measurement if multiple exist on the same day
        df = df.sort_values('Date').drop_duplicates(subset=['Date'], keep='last').set_index('Date').dropna(subset=['Water_Level'])

        print(f"✅ Successfully loaded and cleaned real data from {csv_path}. (Total rows: {len(df)})")
        return df

    except FileNotFoundError:
        print(f"CRITICAL ERROR: '{csv_path}' not found. Switching to simulated data.")
        return create_simulated_data()
    except Exception as e:
        print(f"FATAL ERROR during real data loading/cleaning: {e}")
        print("\nHINT: If the error persists, ensure 'raw_data.csv' is saved as a true plain-text CSV.")
        return create_simulated_data()


def load_and_engineer_data():
    df = load_real_data()

    if df is None or df.empty:
        return

    # --- 2. HANDLE MULTI-STATION DATA (Filter to the most frequent station) ---
    if len(df[['Lat', 'Lon']].drop_duplicates()) > 1:
        # Count occurrences of each (Lat, Lon) pair
        station_counts = Counter(zip(df['Lat'], df['Lon']))
        # Get the coordinates of the most frequent station
        most_frequent_station = station_counts.most_common(1)[0][0]

        df = df[(df['Lat'] == most_frequent_station[0]) & (df['Lon'] == most_frequent_station[1])].copy()

        print(f"⚠️ Data filtered to single station at: Lat {most_frequent_station[0]}, Lon {most_frequent_station[1]}. (Rows remaining: {len(df)})")

    # --- 3. FEATURE ENGINEERING ---
    df['Prev_Level'] = df['Water_Level'].shift(1)
    df['Rainfall_7day'] = df['Rainfall_mm'].rolling(window=7).sum()
    df['Rainfall_30days'] = df['Rainfall_mm'].rolling(window=30).sum()
    df['PET_30days'] = df['PET_mm'].rolling(window=30).sum()
    df['Target_Recharge'] = df['Water_Level'].diff(-30).fillna(0) # 30-day level change

    # Categorical Encoding
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    # Ensure categorical columns are handled correctly
    df_to_encode = df[['Soil_Type', 'LULC']].fillna(df[['Soil_Type', 'LULC']].mode().iloc[0])
    encoded_features = encoder.fit_transform(df_to_encode)

    encoded_df = pd.DataFrame(encoded_features, index=df.index,
                              columns=encoder.get_feature_names_out(['Soil_Type', 'LULC']))

    # Remove original categorical columns and merge encoded ones
    df = df.drop(columns=['Soil_Type', 'LULC'])
    df = pd.concat([df, encoded_df], axis=1).dropna()

    # Save the prepared data and encoder
    df.to_csv('prepared_data.csv')
    joblib.dump(encoder, 'ohe_encoder.pkl')

    print("-------------------------------------------------------")
    print(f"✅ Data pipeline finished. File created: {os.path.abspath('prepared_data.csv')}")
    print("-------------------------------------------------------")
    return df


if __name__ == '__main__':
    load_and_engineer_data()