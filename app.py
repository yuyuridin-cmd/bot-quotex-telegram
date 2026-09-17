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

def get_data():
    ganancia = config["saldo"] - config["base"]
    total = config["wins"] + config["loss"]
    efect = int((config["wins"] / total * 100)) if total > 0 else 0
    saldo = config["saldo"]
    return {
        "saldo": saldo,
        "balance": saldo,
        "saldoDisponible": saldo,
        "disponible": saldo,
        "saldo_disponible": saldo,
        "base": config["base"],
        "base_hoy": config["base"],
        "ganancia": ganancia,
        "ganancia_hoy": ganancia,
        "profit": ganancia,
        "wins": config["wins"],
        "ganadas": config["wins"],
        "ganadasHoy": config["wins"],
        "loss": config["loss"],
        "perdidas": config["loss"],
        "perdidasHoy": config["loss"],
        "efectividad": efect,
        "porcentaje": efect,
        "monto": config["monto_pct"],
        "monto_pct": config["monto_pct"],
        "porcentajeMonto": config["monto_pct"],
        "limite_gana": config["limite_gana"],
        "limiteGanancia": config["limite_gana"],
        "limite_perdida": config["limite_perdida"],
        "limitePerdida": config["limite_perdida"],
        "modo": config["modo"],
        "mode": config["modo"],
        "tipo": config["modo"],
        "accountType": config["modo"],
        "activo": config["activo"],
        "isActive": config["activo"]
    }

@app.route('/api/status')
def status():
    return jsonify(get_data())

@app.route('/api/balance')
def balance():
    return jsonify(get_data())

@app.route('/api/data')
def data():
    return jsonify(get_data())

@app.route('/api/info')
def info():
    return jsonify(get_data())

@app.route('/api/start', methods=['GET', 'POST'])
def start():
    config["activo"] = True
    config["base"] = config["saldo"]
    return jsonify(get_data())

@app.route('/api/stop', methods=['GET', 'POST'])
def stop():
    config["activo"] = False
    return jsonify(get_data())

@app.route('/api/config', methods=['GET', 'POST'])
def cfg():
    d = request.get_json(silent=True) or request.args
    if d:
        if "monto" in d:
            config["monto_pct"] = int(float(d["monto"]))
        if "monto_pct" in d:
            config["monto_pct"] = int(float(d["monto_pct"]))
        if "limite_gana" in d:
            config["limite_gana"] = float(d["limite_gana"])
        if "limite_perdida" in d:
            config["limite_perdida"] = float(d["limite_perdida"])
        if "modo" in d:
            config["modo"] = str(d["modo"]).upper()
        if "mode" in d:
            config["modo"] = str(d["mode"]).upper()
    return jsonify(get_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
