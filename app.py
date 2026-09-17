import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

PORT = 10000

config = {
    "saldo": 115722.81,
    "base": 115722.81,
    "wins": 0,
    "loss": 0,
    "monto_pct": 6,
    "limite_gana": 10,
    "limite_perdida": 10,
    "modo": "DEMO",
    "activo": False
}

app = Flask(__name__, static_folder='webapp')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('webapp', 'index.html')

@app.route('/<path:path>')
def files(path):
    return send_from_directory('webapp', path)

@app.route('/api/status')
def status():
    ganancia = config["saldo"] - config["base"]
    total = config["wins"] + config["loss"]
    efect = int((config["wins"] / total * 100)) if total > 0 else 0
    return jsonify({
        "saldo": config["saldo"],
        "base": config["base"],
        "ganancia": ganancia,
        "wins": config["wins"],
        "loss": config["loss"],
        "efectividad": efect,
        "monto_pct": config["monto_pct"],
        "limite_gana": config["limite_gana"],
        "limite_perdida": config["limite_perdida"],
        "modo": config["modo"],
        "activo": config["activo"]
    })

@app.route('/api/start', methods=['POST'])
def start():
    config["activo"] = True
    config["base"] = config["saldo"]
    return jsonify({"ok": True})

@app.route('/api/stop', methods=['POST'])
def stop():
    config["activo"] = False
    return jsonify({"ok": True})

@app.route('/api/config', methods=['POST'])
def cfg():
    data = request.get_json()
    if data:
        if "monto_pct" in data:
            config["monto_pct"] = int(data["monto_pct"])
        if "limite_gana" in data:
            config["limite_gana"] = float(data["limite_gana"])
        if "limite_perdida" in data:
            config["limite_perdida"] = float(data["limite_perdida"])
        if "modo" in data:
            config["modo"] = data["modo"]
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
