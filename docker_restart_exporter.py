from flask import Flask, Response
import subprocess

app = Flask(__name__)

def get_restart_count(container_name):
    try:
        result = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.RestartCount}}", container_name],
            stderr=subprocess.DEVNULL
        )
        return int(result.decode().strip())
    except Exception:
        return 0

@app.route("/metrics")
def metrics():
    containers = ["demo_app", "metrics_exporter", "cadvisor"]  # add your container names here
    output = []
    for c in containers:
        count = get_restart_count(c)
        output.append(f'docker_container_restart_count{{container="{c}"}} {count}')
    return Response("\n".join(output), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100)
