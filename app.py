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

def get_data():
    ganancia = config["saldo"] - config["base"]
    total = config["wins"] + config["loss"]
    efect = int((config["wins"] / total * 100)) if total > 0 else 0
    return {
        "saldo": config["saldo"],
        "balance": config["saldo"],
        "saldoDisponible": config["saldo"],
        "base": config["base"],
        "ganancia": ganancia,
        "wins": config["wins"],
        "loss": config["loss"],
        "ganadas": config["wins"],
        "perdidas": config["loss"],
        "efectividad": efect,
        "monto": config["monto_pct"],
        "monto_pct": config["monto_pct"],
        "limite_gana": config["limite_gana"],
        "limite_perdida": config["limite_perdida"],
        "modo": config["modo"],
        "mode": config["modo"],
        "activo": config["activo"]
    }

@app.route('/')
def index():
    return send_from_directory('webapp', 'index.html')

@app.route('/<path:path>')
def files(path):
    # Si pide api, no busques archivo
    if path.startswith('api/'):
        return jsonify(get_data())
    return send_from_directory('webapp', path)

@app.route('/api/balance')
def bal(): return jsonify(get_data())
@app.route('/api/stats')
def stats(): return jsonify(get_data())
@app.route('/api/status')
def status(): return jsonify(get_data())
@app.route('/api/data')
def data(): return jsonify(get_data())

@app.route('/api/start', methods=['GET','POST'])
def start():
    config["activo"] = True
    config["base"] = config["saldo"]
    return jsonify(get_data())

@app.route('/api/stop', methods=['GET','POST'])
def stop():
    config["activo"] = False
    return jsonify(get_data())

@app.route('/api/config', methods=['GET','POST'])
def cfg():
    d = request.get_json(silent=True) or request.args or {}
    if "monto" in d: config["monto_pct"] = int(float(d["monto"]))
    if "monto_pct" in d: config["monto_pct"] = int(float(d["monto_pct"]))
    return jsonify(get_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
