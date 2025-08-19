import os
import zipfile
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import requests
import joblib
import logging
from keras.models import load_model

# ====================
# = Constants =
# ====================
DATA_DIR = "data/"
MODELS_DIR = "models/"
DEFAULT_CITY = "Bangalore"

# ====================
# = Load Raw AQI Data =
# ====================
def load_main_data(
    path: str = os.path.join(DATA_DIR, "final_aqi.zip"),
    csv_name: str = "final_aqi.csv"
) -> pd.DataFrame:
    """
    Load the main AQI dataset from a zip archive if necessary.
    Ensures CSV exists locally before reading.
    """
    extract_path = DATA_DIR
    csv_path = os.path.join(extract_path, csv_name)

    # Extract from zip if CSV not found
    if not os.path.exists(csv_path):
        try:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extract(csv_name, path=extract_path)
        except Exception as e:
            logging.error(f"Failed to extract {csv_name} from {path}: {e}")
            return pd.DataFrame()

    # Read CSV and sort by datetime
    try:
        df = pd.read_csv(csv_path, parse_dates=['datetime'])
        df.sort_values("datetime", inplace=True)
        return df
    except Exception as e:
        logging.error(f"Failed to load or parse {csv_path}: {e}")
        return pd.DataFrame()


# ==========================
# = Preprocess for Classifier =
# ==========================
def preprocess_input(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert input pollutant values dict into a DataFrame with required columns.
    """
    df = pd.DataFrame([data])
    columns_needed = ['pm2.5', 'co', 'pm10', 'no2', 'o3', 'so2']
    return df[columns_needed]


# ================================================
# = Robust Live Weather Fetching (WeatherAPI) =
# ================================================
WEATHERAPI_KEY = "c29a1583e9d54bf180f180516250106"
WEATHER_URL_TEMPLATE = "https://api.weatherapi.com/v1/current.json?key={}&q={}"

def fetch_live_weather(
    city: str = DEFAULT_CITY,
    api_key: str = WEATHERAPI_KEY,
) -> Dict[str, Any]:
    """
    Fetch live weather details for the given city from WeatherAPI.
    Returns relevant weather parameters or an error message.
    """
    try:
        url = WEATHER_URL_TEMPLATE.format(api_key, city)
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code == 200 and "current" in data:
            current = data["current"]
            return {
                "city": city,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": datetime.now().strftime('%H:%M:%S'),
                "temp": current.get("temp_c", "--"),
                "humidity": current.get("humidity", "--"),
                "wind": current.get("wind_kph", "--"),
                "description": current.get("condition", {}).get("text", "--").title()
            }
        else:
            msg = data.get("error", {}).get("message", f"Status {response.status_code}")
            print(f"[fetch_live_weather] Error for '{city}': {msg}")
            return {"error": msg}
    except Exception as e:
        print(f"[fetch_live_weather] Exception for '{city}': {e}")
        return {"error": str(e)}


# ====================================================
# = Live AQI Fetch via AQICN (Bangalore only example) =
# ====================================================
AQICN_TOKEN = "5a6f4dac99772929dfbac30bb2984b0f937444a4"  # AQICN API token
AQICN_BANGALORE_URL = f"https://api.waqi.info/feed/bangalore/?token={AQICN_TOKEN}"

def fetch_live_aqi_aqicn() -> Optional[int]:
    """
    Fetch live AQI specifically for Bangalore from AQICN (World Air Quality Index API).
    Returns int AQI value, or None on error.
    """
    try:
        resp = requests.get(AQICN_BANGALORE_URL, timeout=10).json()
        if resp.get("status") == "ok":
            return resp["data"]["aqi"]
        else:
            logging.error(f"[fetch_live_aqi_aqicn] API error for Bangalore: {resp}")
            return None
    except Exception as e:
        logging.error(f"[fetch_live_aqi_aqicn] Exception for Bangalore: {e}")
        return None


# ======================================================
# = Simulate Last 24h Pollutant Feature Data (for LSTM) =
# ======================================================
def simulate_last_24h_features(base_row: Dict[str, float], hours: int = 24) -> pd.DataFrame:
    """
    Simulate plausible last 24 hours pollutant values using Gaussian noise
    around provided base values.
    """
    np.random.seed(42)
    data = {}

    for feat in ['pm2.5', 'co', 'pm10', 'no2', 'o3', 'so2']:
        val = base_row.get(feat, 10.0)
        if feat == "co":
            noise = np.random.normal(0, 0.05, hours)
        else:
            noise = np.random.normal(0, 2, hours)
        series = np.clip(val + np.cumsum(noise), 1, 500)
        data[feat] = series

    timestamps = pd.date_range(end=datetime.now(), periods=hours, freq='h')
    df = pd.DataFrame(data)
    df["datetime"] = timestamps
    return df

def get_latest_data_for_lstm(input_row: Dict[str, float]) -> np.ndarray:
    """
    Simulate last 24h data and normalize each feature to mean 0 and std 1.
    Returns tensor shaped for LSTM input: (1, 24, 6)
    """
    df_24h = simulate_last_24h_features(input_row)
    features = ['pm2.5', 'co', 'pm10', 'no2', 'o3', 'so2']
    normed_cols = []

    for feat in features:
        x = df_24h[feat].values
        std = x.std()
        mean = x.mean()
        if std > 0:
            normed = (x - mean) / std
        else:
            normed = x - mean
        normed_cols.append(normed)

    normed_2d = np.stack(normed_cols, axis=-1)  # Shape (24, 6)
    return normed_2d.reshape(1, 24, 6)


# ====================================================
# = Improved Prediction Functions with Model Caching =
# ====================================================
_lstm_model_global = None
_classifier_model_global = None
AQI_MIN, AQI_MAX = 0.0, 500.0  # Adjust based on training scaling

def _load_lstm():
    """Lazily load and cache the LSTM model."""
    global _lstm_model_global
    if _lstm_model_global is None:
        _lstm_model_global = load_model(os.path.join(MODELS_DIR, "lstm_aqi_model.keras"))
    return _lstm_model_global

def _load_classifier():
    """Lazily load and cache the classifier model."""
    global _classifier_model_global
    if _classifier_model_global is None:
        _classifier_model_global = joblib.load(os.path.join(MODELS_DIR, "classifier.pkl"))
    return _classifier_model_global

def predict_future_aqi(features_24h: np.ndarray) -> Optional[float]:
    """
    Predict the future AQI value from normalized 24h features.
    LSTM output is assumed scaled to [0, 1] — apply inverse scaling.
    """
    try:
        model = _load_lstm()
        pred_scaled = model.predict(features_24h, verbose=0)[0][0]
        pred_actual = pred_scaled * (AQI_MAX - AQI_MIN) + AQI_MIN
        return float(pred_actual)
    except Exception as e:
        logging.error(f"LSTM prediction failed: {e}")
        return None


# =================================
# = Hardcoded AQI → Category map =
# =================================
def predict_category(X: pd.DataFrame) -> str:
    """
    Map AQI value in DataFrame to category string.
    Expects column 'AQI' or first numeric column containing value.
    """
    try:
        if 'AQI' in X.columns:
            aqi = float(X['AQI'].iloc[0])
        else:
            aqi = float(X.iloc[0, 0])

        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Satisfactory"
        elif aqi <= 200:
            return "Moderate"
        elif aqi <= 300:
            return "Poor"
        elif aqi <= 400:
            return "Very Poor"
        else:
            return "Severe"
    except Exception as e:
        logging.error(f"Hardcoded category mapping failed: {e}")
        return "Unknown"


# =====================
# = Model Load Helpers =
# =====================
def load_lstm_model(path: str = os.path.join(MODELS_DIR, "lstm_aqi_model.keras")):
    """Directly load LSTM model from file (no caching)."""
    try:
        return load_model(path)
    except Exception as e:
        logging.error(f"Failed to load LSTM model: {e}")
        return None

def load_classifier_model(path: str = os.path.join(MODELS_DIR, "classifier.pkl")):
    """Directly load classifier model from file (no caching)."""
    try:
        return joblib.load(path)
    except Exception as e:
        logging.error(f"Failed to load classifier model: {e}")
        return None


# =============================
# = Placeholder: Preprocessing =
# =============================
def preprocess_input_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Placeholder for any feature scaling or preprocessing
    to be applied before model prediction (if needed).
    """
    return df
