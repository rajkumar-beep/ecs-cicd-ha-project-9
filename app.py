from flask import Flask, render_template_string, request
import os
import socket
import datetime

app = Flask(__name__)

def get_private_ip():
    try:
        # Connect to external address to find local IP (doesn't send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unavailable"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ECS Node Info</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a0e1a; --surface: #0f1526; --border: #1e2a45;
    --accent: #00e5ff; --accent2: #7b61ff; --green: #00ff88;
    --warn: #ffb800; --text: #e2e8f0; --muted: #4a5568;
  }
  body { background: var(--bg); color: var(--text); font-family: 'Syne', sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
  body::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px); background-size: 40px 40px; animation: gridMove 20s linear infinite; pointer-events: none; }
  @keyframes gridMove { 0%{transform:translateY(0)} 100%{transform:translateY(40px)} }
  .orb { position: fixed; border-radius: 50%; filter: blur(80px); opacity: 0.12; pointer-events: none; animation: pulse 6s ease-in-out infinite alternate; }
  .orb-1 { width:400px; height:400px; background:var(--accent); top:-100px; right:-100px; }
  .orb-2 { width:300px; height:300px; background:var(--accent2); bottom:-80px; left:-80px; animation-delay:-3s; }
  @keyframes pulse { from{opacity:0.08;transform:scale(1)} to{opacity:0.18;transform:scale(1.1)} }
  .card { position:relative; background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:40px; width:520px; max-width:95vw; box-shadow:0 0 0 1px rgba(0,229,255,0.05),0 24px 64px rgba(0,0,0,0.5); animation:slideUp 0.6s cubic-bezier(0.16,1,0.3,1) both; }
  @keyframes slideUp { from{opacity:0;transform:translateY(30px)} to{opacity:1;transform:translateY(0)} }
  .card::before { content:''; position:absolute; top:0; left:20px; right:20px; height:1px; background:linear-gradient(90deg,transparent,var(--accent),transparent); }
  .header { display:flex; align-items:center; gap:14px; margin-bottom:32px; }
  .status-dot { width:10px; height:10px; border-radius:50%; background:var(--green); box-shadow:0 0 10px var(--green); animation:blink 2s ease-in-out infinite; flex-shrink:0; }
  @keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 10px var(--green)} 50%{opacity:0.4;box-shadow:0 0 4px var(--green)} }
  .title { font-size:11px; font-family:'JetBrains Mono',monospace; letter-spacing:3px; text-transform:uppercase; color:var(--muted); margin-bottom:2px; }
  .big-label { font-size:22px; font-weight:800; color:var(--text); }
  .az-badge { margin-left:auto; background:rgba(0,229,255,0.08); border:1px solid rgba(0,229,255,0.2); color:var(--accent); font-family:'JetBrains Mono',monospace; font-size:11px; padding:5px 12px; border-radius:20px; letter-spacing:1px; }
  .divider { height:1px; background:var(--border); margin:0 0 28px; }
  .info-grid { display:grid; gap:14px; }
  .info-row { display:flex; align-items:flex-start; gap:12px; padding:14px 16px; background:rgba(255,255,255,0.02); border:1px solid var(--border); border-radius:10px; transition:border-color 0.2s; animation:slideUp 0.6s cubic-bezier(0.16,1,0.3,1) both; }
  .info-row:nth-child(1){animation-delay:0.1s} .info-row:nth-child(2){animation-delay:0.15s} .info-row:nth-child(3){animation-delay:0.2s} .info-row:nth-child(4){animation-delay:0.25s} .info-row:nth-child(5){animation-delay:0.3s} .info-row:nth-child(6){animation-delay:0.35s}
  .info-row:hover { border-color:rgba(0,229,255,0.2); }
  .icon { font-size:16px; margin-top:1px; flex-shrink:0; }
  .info-content { flex:1; }
  .info-label { font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin-bottom:4px; }
  .info-value { font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:700; color:var(--text); word-break:break-all; }
  .info-value.highlight{color:var(--accent)} .info-value.green{color:var(--green)} .info-value.purple{color:var(--accent2)} .info-value.warn{color:var(--warn)}
  .footer { margin-top:28px; display:flex; align-items:center; justify-content:space-between; }
  .footer-text { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); letter-spacing:1px; }
  .version-pill { background:rgba(123,97,255,0.12); border:1px solid rgba(123,97,255,0.25); color:var(--accent2); font-family:'JetBrains Mono',monospace; font-size:11px; padding:4px 12px; border-radius:20px; }
</style>
</head>
<body>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="card">
  <div class="header">
    <div class="status-dot"></div>
    <div>
      <div class="title">AWS ECS Fargate</div>
      <div class="big-label">Node Info</div>
    </div>
    <div class="az-badge">{{ az }}</div>
  </div>
  <div class="divider"></div>
  <div class="info-grid">
    <div class="info-row">
      <div class="icon">🌐</div>
      <div class="info-content">
        <div class="info-label">Availability Zone</div>
        <div class="info-value highlight">{{ az }}</div>
      </div>
    </div>
    <div class="info-row">
      <div class="icon">📦</div>
      <div class="info-content">
        <div class="info-label">Container Hostname</div>
        <div class="info-value green">{{ hostname }}</div>
      </div>
    </div>
    <div class="info-row">
      <div class="icon">🔗</div>
      <div class="info-content">
        <div class="info-label">Private IP Address</div>
        <div class="info-value">{{ task_ip }}</div>
      </div>
    </div>
    <div class="info-row">
      <div class="icon">🚀</div>
      <div class="info-content">
        <div class="info-label">App Version</div>
        <div class="info-value purple">{{ version }}</div>
      </div>
    </div>
    <div class="info-row">
      <div class="icon">🕐</div>
      <div class="info-content">
        <div class="info-label">Request Time (UTC)</div>
        <div class="info-value warn">{{ timestamp }}</div>
      </div>
    </div>
  </div>
  <div class="footer">
    <div class="footer-text">ECS HA Demo · Project 9</div>
    <div class="version-pill">{{ version }}</div>
  </div>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML,
        az        = os.environ.get("AZ", "ap-south-1a"),
        hostname  = socket.gethostname(),
        task_ip   = get_private_ip(),
        version   = os.environ.get("APP_VERSION", "v1.0.0"),
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
