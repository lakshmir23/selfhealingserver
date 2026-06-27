import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_model.pkl")

def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Load metrics dataset
    df = pd.read_csv("data/metrics.csv")

    # Use CPU, RAM, Disk columns (make sure metrics.csv has these headers)
    X = df[["cpu_usage", "ram_usage", "disk_usage"]].values

    # Train Isolation Forest
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X)

    # Save trained model
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model trained and saved at {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
