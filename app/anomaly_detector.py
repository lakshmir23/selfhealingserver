import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from app.config import (
    MODEL_PATH,
    CPU_THRESHOLD,
    RAM_THRESHOLD,
    DISK_THRESHOLD,
)
from app.logger import log_event


def train_model(training_data: list) -> IsolationForest:
    """
    Train an Isolation Forest model using historical metrics.
    """

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    X = np.array(training_data)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.01,      # Less sensitive
        random_state=42
    )

    model.fit(X)

    joblib.dump(model, MODEL_PATH)

    log_event(
        "MODEL",
        f"Isolation Forest trained on {len(X)} samples and saved."
    )

    return model


def load_model():
    """
    Load the saved Isolation Forest model.
    """

    if os.path.exists(MODEL_PATH):
        log_event("MODEL", "Pre-trained model loaded.")
        return joblib.load(MODEL_PATH)

    log_event(
        "MODEL",
        "No pre-trained model found. Will train a new model.",
        "WARN"
    )

    return None


def is_anomaly(cpu, ram, disk, model=None):
    """
    Detect anomalies using the ML model.
    Falls back to threshold detection if no model exists.
    """

    if model is not None:

        sample = np.array([[cpu, ram, disk]])

        prediction = model.predict(sample)

        result = prediction[0] == -1

        # Debug prints
        print("\n========== MODEL DEBUG ==========")
        print(f"CPU  : {cpu:.1f}%")
        print(f"RAM  : {ram:.1f}%")
        print(f"DISK : {disk:.1f}%")
        print(f"Prediction : {prediction[0]}")
        print(f"Anomaly   : {result}")
        print("=================================\n")

        log_event(
            "ANOMALY",
            f"ML Detection - CPU:{cpu:.1f} RAM:{ram:.1f} DISK:{disk:.1f} -> {'ANOMALY' if result else 'NORMAL'}"
        )

        return result

    # Threshold fallback
    result = (
        cpu > CPU_THRESHOLD
        or ram > RAM_THRESHOLD
        or disk > DISK_THRESHOLD
    )

    log_event(
        "ANOMALY",
        f"Threshold Detection - CPU:{cpu:.1f} RAM:{ram:.1f} DISK:{disk:.1f} -> {'ANOMALY' if result else 'NORMAL'}"
    )

    return result


def generate_synthetic_training_data(n_samples=1000):
    """
    Generate realistic system metrics for initial model training.
    """

    np.random.seed(42)

    data = []

    for _ in range(n_samples):

        cpu = np.random.uniform(0, 85)

        ram = np.random.uniform(20, 90)

        disk = np.random.uniform(20, 95)

        data.append([cpu, ram, disk])

    return data