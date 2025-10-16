import pandas as pd
import joblib
from pathlib import Path

# --- Model Loading ---
# Build a path to the model file relative to this script
MODEL_PATH = Path(__file__).parents[2] / "models" / "global_lgbm_model.pkl"
MODEL = None

def load_model():
    """Loads the LightGBM model from the .pkl file into memory."""
    global MODEL
    if MODEL is None:
        try:
            MODEL = joblib.load(MODEL_PATH)
            print("Forecasting model loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Model file not found at {MODEL_PATH}")
            MODEL = None
    return MODEL

# --- Feature Engineering ---
def create_features_for_prediction(dates, store_id, item_id):
    """
    Creates the same features your model was trained on for future dates.
    NOTE: You may need to adjust this to match your model's exact features.
    """
    df = pd.DataFrame({'date': dates})
    df['store'] = store_id
    df['item'] = item_id
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    # Add any other features your model expects (e.g., weekofyear, dayofyear)
    
    # Ensure columns are in the correct order the model expects
    # This is a common feature set, adjust if yours is different.
    feature_columns = ['store', 'item', 'year', 'month', 'day', 'dayofweek'] 
    return df[feature_columns]

# --- Prediction ---
def predict_sales_with_lgbm(store_id: int, item_id: int, days_to_forecast: int = 10):
    """
    Generates sales forecasts using the pre-trained LightGBM model.
    """
    model = load_model()
    if model is None:
        return None

    # 1. Create future dates
    future_dates = pd.to_datetime(pd.to_datetime('today').date()) + pd.to_timedelta(range(1, days_to_forecast + 1), unit='d')
    
    # 2. Engineer features for those dates
    features_df = create_features_for_prediction(future_dates, store_id, item_id)
    
    # 3. Make predictions
    predictions = model.predict(features_df)
    
    # 4. Format the output
    forecast_results = {
        "dates": [d.strftime('%Y-%m-%d') for d in future_dates],
        "predicted_sales": [round(p, 2) for p in predictions]
    }
    
    return forecast_results