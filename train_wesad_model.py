"""
Train and serialize the WESAD Multi-Modal Physiological ML Model.
Features: [mean_hr, rmssd_hrv, mean_temp, temp_slope, mean_eda]
Labels: 0 (Normal Baseline), 1 (Acute Stress / Heat Exhaustion)
"""

import sys
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def generate_synthetic_wesad_data(n_samples: int = 2000):
    """
    Generate physiologically realistic WESAD multi-modal features.
    """
    np.random.seed(42)

    # 1. Baseline / Normal State (Label 0)
    normal_hr = np.random.normal(72, 6, n_samples // 2)
    normal_rmssd = np.random.normal(45, 10, n_samples // 2)  # High HRV = Relaxed/Parasympathetic
    normal_temp = np.random.normal(36.8, 0.3, n_samples // 2)
    normal_slope = np.random.normal(0.0, 0.02, n_samples // 2)
    normal_eda = np.random.normal(1.5, 0.4, n_samples // 2)  # Normal Galvanic Skin Response
    labels_normal = np.zeros(n_samples // 2)

    # 2. Acute Stress / Heat Exhaustion State (Label 1)
    stress_hr = np.random.normal(125, 12, n_samples // 2)
    stress_rmssd = np.random.normal(18, 5, n_samples // 2)   # Depressed HRV = Severe Stress
    stress_temp = np.random.normal(39.1, 0.6, n_samples // 2)
    stress_slope = np.random.normal(0.15, 0.05, n_samples // 2)  # Rapid core temperature rise
    stress_eda = np.random.normal(8.5, 2.1, n_samples // 2)      # High sympathetic arousal
    labels_stress = np.ones(n_samples // 2)

    X = np.vstack([
        np.column_stack([normal_hr, normal_rmssd, normal_temp, normal_slope, normal_eda]),
        np.column_stack([stress_hr, stress_rmssd, stress_temp, stress_slope, stress_eda])
    ])
    y = np.concatenate([labels_normal, labels_stress])
    return X, y


def train_and_export():
    print("[+] Training WESAD Multi-Feature Physiological Model...")
    X, y = generate_synthetic_wesad_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\n--- Model Evaluation Report ---")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Physiological Anomaly"]))

    model_path = "wesad_model.joblib"
    joblib.dump(clf, model_path)
    print(f"[+] Model successfully serialized to {model_path}")
    return clf


if __name__ == "__main__":
    train_and_export()
