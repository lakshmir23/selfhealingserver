from plyer import notification
from app.logger import log_event

APP_NAME = "Self-Healing Server"


def desktop_notify(title: str, message: str):
    """Send a desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            timeout=10
        )
        log_event("NOTIFICATION", f"Desktop notification sent: {title}")
    except Exception as e:
        log_event("NOTIFICATION", f"Desktop notification failed: {e}", "ERROR")


def notify_alert(message: str):
    desktop_notify(
        "Self-Healing Alert",
        message
    )


def notify_success(message: str):
    desktop_notify(
        "Self-Healing Success",
        message
    )


def notify_failure(message: str):
    desktop_notify(
        "Self-Healing Failure",
        message
    )