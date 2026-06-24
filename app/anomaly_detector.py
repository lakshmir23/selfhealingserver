import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from app.config import MODEL_PATH
from app.logger import log_event
import csv
from app.config import METRICS_FILE


def load_real_training_data(min_samples: int = 20) -> list | None:
    """Load real metrics from CSV for training. Returns None if not enough data."""
    if not os.path.exists(METRICS_FILE):
        return None

    data = []
    with open(METRICS_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                cpu, ram, disk = float(row[1]), float(row[2]), float(row[3])
                data.append([cpu, ram, disk])
            except (IndexError, ValueError):
                continue

    if len(data) < min_samples:
        return None
    return data


def train_model(training_data: list) -> IsolationForest:
    """
    Train an Isolation Forest model on historical metrics.
    training_data: list of [cpu, ram, disk] samples.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    X = np.array(training_data)
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    log_event("MODEL", f"Isolation Forest trained on {len(X)} samples and saved.")
    return model


def load_model() -> IsolationForest | None:
    """Load a previously saved model. Returns None if not found."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    log_event("MODEL", "No pre-trained model found. Will use threshold-based detection.", "WARN")
    return None


def is_anomaly(cpu: float, ram: float, disk: float, model: IsolationForest = None) -> bool:
    """
    Detect if the current metrics represent an anomaly.
    Falls back to simple threshold checks if no model is loaded.
    """
    if model:
        sample = np.array([[cpu, ram, disk]])
        prediction = model.predict(sample)
        # IsolationForest: -1 = anomaly, 1 = normal
        result = prediction[0] == -1
        log_event("ANOMALY", f"ML Detection — CPU:{cpu} RAM:{ram} DISK:{disk} -> {'ANOMALY' if result else 'Normal'}")
        return result
    else:
        # Fallback: simple threshold check
        from app.config import CPU_THRESHOLD, RAM_THRESHOLD, DISK_THRESHOLD
        result = cpu > CPU_THRESHOLD or ram > RAM_THRESHOLD or disk > DISK_THRESHOLD
        log_event("ANOMALY", f"Threshold Detection — CPU:{cpu} RAM:{ram} DISK:{disk} -> {'ANOMALY' if result else 'Normal'}")
        return result


def generate_synthetic_training_data(n_samples: int = 500) -> list:
    np.random.seed(42)
    data = []
    for _ in range(n_samples):
        cpu = np.random.uniform(0, 5)
        ram = np.random.uniform(10, 25)
        disk = np.random.uniform(0, 2)
        data.append([cpu, ram, disk])
    return data