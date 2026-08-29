"""
Train a clinical conjunctival pallor / erythema Hemoglobin regression model.
Based on non-invasive conjunctival digital imaging benchmarks:
  - Mannino et al., 2017 (Smartphone app for non-invasive hemoglobin estimation)
  - Suner et al., 2007 (Conjunctival pallor analysis for anemia detection)

Trains a GradientBoostingRegressor predicting Hb in g/dL from:
  1. erythema_index (vascular contrast)
  2. r_channel_mean (red chrominance mean)
  3. g_channel_mean (green absorption)
  4. b_channel_mean (blue absorption)
  5. red_green_ratio (hemoglobin spectral reflectance ratio)
"""
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

FEATURES = ["erythema_index", "r_channel_mean", "g_channel_mean", "b_channel_mean", "red_green_ratio"]

def generate_anemia_dataset(n_samples=2500):
    rng = np.random.RandomState(42)
    # True Hemoglobin distribution: 5.0 to 18.0 g/dL
    hb_true = rng.uniform(5.5, 17.5, size=n_samples)
    
    # Physical optical relationships
    # Higher Hb -> higher erythema, higher R channel, lower G/B absorption
    erythema = np.clip(0.05 + (hb_true - 5.0) * 0.08 + rng.normal(0, 0.04, size=n_samples), 0.01, 1.0)
    r_mean = np.clip(80 + (hb_true - 5.0) * 9.5 + rng.normal(0, 6.0, size=n_samples), 40, 240)
    g_mean = np.clip(130 - (hb_true - 5.0) * 4.0 + rng.normal(0, 5.0, size=n_samples), 50, 200)
    b_mean = np.clip(120 - (hb_true - 5.0) * 3.5 + rng.normal(0, 5.0, size=n_samples), 50, 190)
    rg_ratio = np.clip(r_mean / (g_mean + 1e-5) + rng.normal(0, 0.03, size=n_samples), 0.4, 2.5)
    
    X = np.column_stack([erythema, r_mean, g_mean, b_mean, rg_ratio])
    return X, hb_true

def train_and_export(model_path="anemia_model.joblib"):
    X, y = generate_anemia_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = GradientBoostingRegressor(n_estimators=150, max_depth=4, learning_rate=0.08, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    cv = cross_val_score(model, X, y, cv=5, scoring="r2")
    
    metrics = {
        "r2_score": round(r2, 4),
        "mae_g_dl": round(mae, 3),
        "rmse_g_dl": round(rmse, 3),
        "cv_mean_r2": round(cv.mean(), 4),
        "feature_importance": dict(zip(FEATURES, [round(float(x), 4) for x in model.feature_importances_]))
    }
    
    joblib.dump({"model": model, "features": FEATURES, "metrics": metrics}, model_path)
    print(f"[ANEMIA] Model exported to {model_path}")
    print(f"[ANEMIA] R2 Score: {r2:.3f} | MAE: {mae:.2f} g/dL | RMSE: {rmse:.2f} g/dL")
    return model, metrics

if __name__ == "__main__":
    train_and_export()
