import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib


def train_lstm_model():
    df = pd.read_csv('prepared_data.csv', index_col='Date', parse_dates=True)

    FEATURES = ['Water_Level', 'Rainfall_7day', 'PET_mm', 'Avg_Temp_C', 'Prev_Level']

    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df[FEATURES]), columns=FEATURES, index=df.index)
    joblib.dump(scaler, 'lstm_scaler.pkl')

    SEQ_LENGTH = 1
    X, y = [], []
    for i in range(len(df_scaled) - SEQ_LENGTH):
        X.append(df_scaled.iloc[i:(i + SEQ_LENGTH)][FEATURES].values)
        y.append(df['Water_Level'].iloc[i + SEQ_LENGTH])

    X, y = np.array(X), np.array(y)

    split_point = int(0.9 * len(X))
    X_train, y_train = X[:split_point], y[:split_point]

    model = Sequential()
    # Note: input_shape changed to match the features and sequence length
    model.add(LSTM(50, return_sequences=False, input_shape=(SEQ_LENGTH, len(FEATURES))))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    print("Training LSTM Water Fluctuation Model...")
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1, verbose=1)

    # Save model in the recommended native Keras format (.keras)
    file_name = 'lstm_water_level_predictor.keras'
    model.save(file_name)

    print(f"✅ LSTM Model trained and saved successfully.")
    print(f"File created at: {os.path.abspath(file_name)}")


if __name__ == '__main__':
    train_lstm_model()