from flask import Flask, Response
from prometheus_client import Gauge, Counter, generate_latest
import psutil

app = Flask(__name__)

# Metrics
cpu_gauge = Gauge("cpu_usage", "CPU usage")
ram_gauge = Gauge("ram_usage", "RAM usage")
disk_gauge = Gauge("disk_usage", "Disk usage")

restart_count_gauge = Gauge(
    "restart_count",
    "Number of self-healing restarts"
)

health_status_gauge = Gauge(
    "health_status",
    "1 = Healthy, 0 = Unhealthy"
)

anomaly_events_counter = Counter(
    "anomaly_events_total",
    "Total anomalies detected"
)

# Prevent counting the same anomaly repeatedly
anomaly_active = False


def collect_metrics():
    global anomaly_active

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    cpu_gauge.set(cpu)
    ram_gauge.set(ram)
    disk_gauge.set(disk)

    # Health status + anomaly detection
    if cpu > 80 or ram > 85:
        health_status_gauge.set(0)

        if not anomaly_active:
            anomaly_events_counter.inc()
            anomaly_active = True

    else:
        health_status_gauge.set(1)
        anomaly_active = False

    # Restart count
    try:
        with open("data/restart_count.txt", "r") as f:
            restart_count = int(f.read().strip())
    except Exception:
        restart_count = 0

    restart_count_gauge.set(restart_count)


@app.route("/metrics")
def metrics():
    collect_metrics()
    return Response(
        generate_latest(),
        mimetype="text/plain"
    )


@app.route("/health")
def health():
    return {"status": "ok"}


def run_metrics_server():
    print("Metrics server running on port 8000")
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_metrics_server()