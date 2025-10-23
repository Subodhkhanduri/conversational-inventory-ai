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
import pandas as pd
import joblib
from pathlib import Path

# --- Model Loading ---
# ... (this part is fine) ...

# --- Feature Engineering ---
def create_features_for_prediction(dates, store_id, item_id):
    """
    Creates the same features your model was trained on for future dates.
    """
    df = pd.DataFrame({'date': dates})
    df['store'] = store_id
    df['item'] = item_id
    df['date'] = pd.to_datetime(df['date'])
    
    # --- OUR FIRST 8 FEATURES ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['weekofyear'] = df['date'].dt.isocalendar().week
    df['dayofyear'] = df['date'].dt.dayofyear
    
    # --- ADD YOUR 4 MISSING FEATURES HERE ---
    # (These are just GUESSES. You must use YOUR features)
    df['quarter'] = df['date'].dt.quarter
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    
    # Lag features are hard to generate for future dates without
    # historical data. If your model uses them, we may need a
    # more complex approach. Let's assume for now your
    # other features are also date-based.
    df['day_x_month'] = df['day'] * df['month'] 
    df['store_x_item'] = df['store'] * df['item']

    # --- FINAL 12-FEATURE LIST (Must be in order!) ---
    feature_columns = [
        'store', 
        'item', 
        'year', 
        'month', 
        'day', 
        'dayofweek',
        'weekofyear',
        'dayofyear',
        # --- YOUR 4 FEATURES ---
        'quarter',      # (Example)
        'is_weekend',   # (Example)
        'day_x_month',  # (Example)
        'store_x_item', # (Example)
    ] 
    
    # Ensure the DataFrame only has these columns and in this order
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