import docker
import httpx
from app.config import TARGET_CONTAINER
from app.logger import log_event


def is_container_running(container_name: str = TARGET_CONTAINER) -> bool:
    """Check whether the target Docker container is running."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        status = container.status
        log_event("HEALTH", f"Container '{container_name}' status: {status}")
        return status == "running"
    except docker.errors.NotFound:
        log_event("HEALTH", f"Container '{container_name}' not found.", "ALERT")
        return False
    except Exception as e:
        log_event("HEALTH", f"Docker check error: {e}", "ERROR")
        return False

def is_app_responding(url: str = "http://demo_app:8080/health") -> bool:
    """Check if the application HTTP endpoint responds correctly."""
    try:
        response = httpx.get(url, timeout=5)
        if response.status_code == 200:
            log_event("HEALTH", f"App at {url} is responding OK.")
            return True
        else:
            log_event("HEALTH", f"App at {url} returned status {response.status_code}.", "WARN")
            return False
    except Exception as e:
        log_event("HEALTH", f"App not responding at {url}: {e}", "WARN")
        return False


def get_health_status(container_name: str = TARGET_CONTAINER) -> str:
    """Return overall health status: 'healthy', 'unhealthy', or 'unknown'."""
    container_ok = is_container_running(container_name)
    app_ok = is_app_responding()
    if container_ok and app_ok:
        return "healthy"
    elif not container_ok:
        return "container_down"
    else:
        return "app_unresponsive"