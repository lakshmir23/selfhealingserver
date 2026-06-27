import time
import schedule

from app.config import MONITOR_INTERVAL, TARGET_CONTAINER
from app.monitor import collect_metrics
from app.health_check import get_health_status
from app.anomaly_detector import (
    is_anomaly,
    load_model,
    train_model,
    generate_synthetic_training_data,
)
from app.healer import heal
from app.logger import log_metrics, log_event
from app.notifier import notify_alert, notify_success, notify_failure

# Track previous health status
LAST_STATUS = "healthy"


def initialize_model():
    """Load existing model or train a new one with synthetic data."""
    model = load_model()

    if model is None:
        log_event("INIT", "Training a new model with synthetic data...")
        training_data = generate_synthetic_training_data(1000)
        model = train_model(training_data)

    return model


def monitor_cycle(model):
    """One complete monitoring, detection, and healing cycle."""

    global LAST_STATUS

    # -------------------------
    # 1. Collect Metrics
    # -------------------------
    metrics = collect_metrics()
    cpu = metrics["cpu"]
    ram = metrics["ram"]
    disk = metrics["disk"]

    log_event(
        "MONITOR",
        f"CPU:{cpu:.1f}% | RAM:{ram:.1f}% | DISK:{disk:.1f}%"
    )

    # -------------------------
    # 2. Health Check
    # -------------------------
    health = get_health_status(TARGET_CONTAINER)

    # -------------------------
    # 3. Recovery Notification
    # -------------------------
    if LAST_STATUS != "healthy" and health == "healthy":

        print("System has recovered.")

        notify_success(
            f"System recovered!\n\n"
            f"Container : {TARGET_CONTAINER}\n"
            f"Status    : Running\n"
            f"Monitoring resumed successfully."
        )

    LAST_STATUS = health

    # -------------------------
    # 4. ML Detection
    # -------------------------
    anomaly = is_anomaly(cpu, ram, disk, model)

    # -------------------------
    # 5. Save Metrics
    # -------------------------
    log_metrics(cpu, ram, disk, health, anomaly)

    action = "NO_ACTION"

    # -------------------------
    # 6. Self Healing
    # -------------------------
    if health != "healthy" or anomaly:

        reason = (
            f"Container : {TARGET_CONTAINER}\n"
            f"Health    : {health}\n"
            f"Anomaly   : {anomaly}\n"
            f"CPU       : {cpu:.1f}%\n"
            f"RAM       : {ram:.1f}%\n"
            f"DISK      : {disk:.1f}%"
        )

        log_event(
            "ALERT",
            reason,
            "TRIGGERING_HEAL"
        )

        print("\n================================")
        print("ISSUE DETECTED")
        print(reason)
        print("================================\n")

        # Alert Notification
        print("Sending Alert Notification...")
        notify_alert(reason)

        # Restart
        action = heal(
            health,
            anomaly,
            TARGET_CONTAINER
        )

        # Restart Success
        if action == "RESTART_SUCCESS":

            print("Restart Successful.")

            notify_success(
                f"Container '{TARGET_CONTAINER}' restarted successfully."
            )

        # Restart Failed
        elif action == "RESTART_FAILED":

            print("Restart Failed.")

            notify_failure(
                f"Failed to restart container '{TARGET_CONTAINER}'."
            )

    log_event(
        "CYCLE",
        f"Cycle complete. Action: {action}"
    )

    return action


def run():
    """Start the monitoring system."""

    print("=" * 60)
    print("🛡️  Self-Healing Server Monitoring Started")
    print("=" * 60)

    log_event(
        "INIT",
        "Self-Healing Server started."
    )

    model = initialize_model()

    # Run once immediately
    monitor_cycle(model)

    # Schedule future runs
    schedule.every(MONITOR_INTERVAL).seconds.do(
        monitor_cycle,
        model
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run()