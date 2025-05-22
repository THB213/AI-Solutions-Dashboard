# sales_model.py
import pandas as pd
import lightgbm as lgb
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "models" / "sales_model.pkl"

def prepare_ml_data(df):
    """Prepare weekly features from raw sales data"""
    daily_data = df.groupby('date').agg(
        total_sales=('amount', 'sum'),
        num_purchases=('amount', 'count'),
        unique_products=('product', 'nunique'),
        unique_countries=('country', 'nunique')
    ).reset_index()
    
    # Add temporal features
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    daily_data['day_of_week'] = daily_data['date'].dt.dayofweek
    daily_data['week_of_year'] = daily_data['date'].dt.isocalendar().week
    daily_data['month'] = daily_data['date'].dt.month
    daily_data['year'] = daily_data['date'].dt.year
    
    # Create weekly data
    weekly_data = daily_data.resample('W-Mon', on='date').agg({
        'total_sales': 'sum',
        'num_purchases': 'sum',
        'unique_products': 'mean',
        'unique_countries': 'mean',
        'day_of_week': 'mean',
        'week_of_year': 'last',
        'month': 'last',
        'year': 'last'
    }).reset_index()
    
    weekly_data['target'] = weekly_data['total_sales'].shift(-1)
    return weekly_data.dropna()

def train_model(df):
    """Train and save the LGBM model"""
    weekly_data = prepare_ml_data(df)
    X = weekly_data.drop(columns=['date', 'target'])
    y = weekly_data['target']
    
    model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X, y)
    
    # Create models directory if it doesn't exist
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model

def load_model():
    """Load the trained model"""
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None

def get_predictions(df, model=None):
    """Generate predictions for the dashboard"""
    if model is None:
        model = load_model()
    
    weekly_data = prepare_ml_data(df)
    if model:
        weekly_data['predicted'] = model.predict(
            weekly_data.drop(columns=['date', 'target'], errors='ignore')
        )
    return weekly_data