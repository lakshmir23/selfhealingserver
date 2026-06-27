from app.notifier import notify_alert, notify_success, notify_failure

notify_alert("Container 'demo_app' is DOWN.\nRestarting automatically...")

notify_success("Container 'demo_app' restarted successfully.")

notify_failure("Failed to restart 'demo_app'. Manual intervention required.")