import random
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Demo App", version="1.0.0")

start_time = time.time()


@app.get("/")
def root():
    return {"message": "Demo App is running!", "status": "ok"}


@app.get("/health")
def health():
    """Health check endpoint used by the monitoring system."""
    return JSONResponse(status_code=200, content={"status": "healthy"})


@app.get("/metrics")
def metrics():
    """Expose basic app metrics."""
    uptime = time.time() - start_time
    return {
        "uptime_seconds": round(uptime, 2),
        "status": "running",
        "random_load": random.uniform(0, 100)
    }


@app.get("/stress")
def stress():
    """Endpoint to simulate sustained CPU load."""
    import time
    end_time = time.time() + 15  # run for 15 seconds
    result = 0
    while time.time() < end_time:
        result = sum(i * i for i in range(100_000))
    return {"status": "stress_done", "result": result}


@app.get("/crash")
def crash():
    """Simulate an app crash (raises an unhandled error)."""
    raise RuntimeError("Simulated crash for testing self-healing!")