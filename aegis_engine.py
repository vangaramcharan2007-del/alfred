"""
AEGIS Engine - Offline-First Health Companion ML Core
Provides baseline physiological training and anomaly detection using scikit-learn IsolationForest.
"""

from typing import NamedTuple, Dict, Any, Union
import numpy as np
from sklearn.ensemble import IsolationForest


class EvaluationResult(NamedTuple):
    risk_score: str
    is_anomaly: bool
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_score": self.risk_score,
            "is_anomaly": self.is_anomaly,
            "score": self.score
        }


class AnomalyDetector:
    """
    Physiological Anomaly Detector for Heart Rate (BPM) and Body Temperature (°C).
    Trained on healthy baseline distributions using IsolationForest.
    """

    def __init__(self, random_state: int = 42, contamination: float = 0.01, n_samples: int = 1000):
        self.random_state = random_state
        self.contamination = contamination
        self.n_samples = n_samples
        self.model: IsolationForest = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=self.random_state
        )
        self.is_trained: bool = False
        self.train_baseline()

    def train_baseline(self) -> None:
        """
        Train baseline IsolationForest model on healthy resting dummy data:
        - Resting HR: 60 - 80 BPM
        - Body Temp: 36.5 - 37.5 °C
        """
        rng = np.random.default_rng(self.random_state)
        hr_baseline = rng.uniform(60.0, 80.0, self.n_samples)
        temp_baseline = rng.uniform(36.5, 37.5, self.n_samples)

        X_train = np.column_stack([hr_baseline, temp_baseline])
        self.model.fit(X_train)
        self.is_trained = True

    def evaluate(self, hr: Union[int, float], temp: Union[int, float]) -> EvaluationResult:
        """
        Evaluate physiological telemetry and determine anomaly status and risk score.

        Args:
            hr: Heart rate in beats per minute (BPM)
            temp: Body temperature in degrees Celsius (°C)

        Returns:
            EvaluationResult with risk_score ("Normal" / "High") and is_anomaly (bool)
        """
        if not self.is_trained:
            self.train_baseline()

        hr_val = float(hr)
        temp_val = float(temp)
        X_test = np.array([[hr_val, temp_val]])

        # IsolationForest decision: 1 = inlier (Normal), -1 = outlier (Anomaly)
        pred = self.model.predict(X_test)[0]
        decision_score = float(self.model.decision_function(X_test)[0])

        is_anomaly = bool(pred == -1)
        risk_score = "High" if is_anomaly else "Normal"

        return EvaluationResult(
            risk_score=risk_score,
            is_anomaly=is_anomaly,
            score=decision_score
        )
