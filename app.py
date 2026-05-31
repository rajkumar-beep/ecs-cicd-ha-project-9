from flask import Flask, render_template_string
import os
import socket
import datetime
import urllib.request
import json

app = Flask(__name__)

def get_task_ip():
    try:
        metadata_uri = (
            os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
            or os.environ.get("ECS_CONTAINER_METADATA_URI")
        )

        if metadata_uri:
            with urllib.request.urlopen(f"{metadata_uri}/task", timeout=2) as r:
                data = json.loads(r.read())

                for attachment in data.get("Attachments", []):
                    for detail in attachment.get("Details", []):
                        if detail.get("Name") == "privateIPv4Address":
                            return detail.get("Value")

    except Exception:
        pass

    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "unavailable"


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ECS HA Demo</title>

<style>
body {
    background: #0f172a;
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
}

.card {
    width: 600px;
    background: #1e293b;
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.3);
}

h1 {
    text-align: center;
    color: #38bdf8;
}

.row {
    margin: 15px 0;
    padding: 12px;
    background: #334155;
    border-radius: 8px;
}

.label {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
}

.value {
    font-size: 18px;
    font-weight: bold;
    margin-top: 5px;
}

.footer {
    margin-top: 20px;
    text-align: center;
    color: #94a3b8;
}
</style>

</head>

<body>

<div class="card">

<h1>🚀 AWS ECS Fargate Demo</h1>

<div class="row">
<div class="label">Availability Zone</div>
<div class="value">{{ az }}</div>
</div>

<div class="row">
<div class="label">Container Hostname</div>
<div class="value">{{ hostname }}</div>
</div>

<div class="row">
<div class="label">Private IP</div>
<div class="value">{{ task_ip }}</div>
</div>

<div class="row">
<div class="label">Application Version</div>
<div class="value">{{ version }}</div>
</div>

<div class="row">
<div class="label">Request Time (UTC)</div>
<div class="value">{{ timestamp }}</div>
</div>

<div class="footer">
ECS HA Demo | Project 9
</div>

</div>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(
        HTML,
        az=os.environ.get("AZ", "ap-south-1a"),
        hostname=socket.gethostname(),
        task_ip=get_task_ip(),
        version=os.environ.get("APP_VERSION", "v1.0.0"),
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
