import os, threading, time, traceback
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

try:
    from quotexapi.stable_api import Quotex
    HAS_QUOTEX = True
except:
    HAS_QUOTEX = False

PORT = 10000
config = {
    "saldo": 0, "base": 0, "wins": 0, "loss": 0,
    "monto_pct": 6, "limite_gana": 10, "limite_perdida": 10,
    "modo": "DEMO", "activo": False, "conectado": False,
    "email": "", "porcentaje_hoy": 0
}
client = None

def get_data():
    base = config["base"] or config["saldo"] or 1
    ganancia = config["saldo"] - base
    porc = round((ganancia / base * 100) if base>0 else 0, 2)
    total = config["wins"]+config["loss"]
    efect = int((config["wins"]/total*100)) if total>0 else 0
    config["porcentaje_hoy"] = porc
    return {
        "saldo": config["saldo"], "balance": config["saldo"],
        "base": config["base"], "ganancia": ganancia,
        "porcentaje_hoy": porc, "porcentaje": porc,
        "wins": config["wins"], "loss": config["loss"],
        "efectividad": efect, "monto_pct": config["monto_pct"],
        "monto": config["monto_pct"], "modo": config["modo"],
        "conectado": config["conectado"], "email": config["email"],
        "activo": config["activo"]
    }

def loop_saldo():
    while True:
        try:
            if client and config["conectado"]:
                bal = client.get_balance()
                if bal is not None:
                    config["saldo"] = bal
        except: pass
        time.sleep(3)

app = Flask(__name__, static_folder='webapp')
CORS(app)

@app.route('/')
def index(): return send_from_directory('webapp', 'index.html')
@app.route('/<path:path>')
def files(path):
    if path.startswith('api/'): return jsonify(get_data())
    return send_from_directory('webapp', path)

@app.route('/api/balance')
def bal(): return jsonify(get_data())
@app.route('/api/stats')
def stats(): return jsonify(get_data())
@app.route('/api/status')
def status(): return jsonify(get_data())

@app.route('/api/login', methods=['POST'])
def login():
    global client
    try:
        d = request.get_json()
        email = d.get('email','').strip()
        password = d.get('password','').strip()
        modo = d.get('modo','DEMO').upper()
        if not email or not password:
            return jsonify({"ok": False, "error": "Falta correo o clave"})
        if not HAS_QUOTEX:
            return jsonify({"ok": False, "error": "Falta libreria quotexapi"})
        print(f"Conectando {email}...")
        client = Quotex(email=email, password=password)
        check, reason = client.connect()
        if not check:
            return jsonify({"ok": False, "error": f"No conecta: {reason}"})
        try:
            client.change_account("real" if modo=="REAL" else "demo")
        except: pass
        time.sleep(1)
        saldo = client.get_balance()
        config["saldo"] = saldo
        config["base"] = saldo
        config["conectado"] = True
        config["email"] = email
        config["modo"] = modo
        threading.Thread(target=loop_saldo, daemon=True).start()
        return jsonify({"ok": True, **get_data()})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})

@app.route('/api/logout', methods=['POST'])
def logout():
    global client
    config["conectado"] = False
    config["email"] = ""
    config["saldo"] = 0
    client = None
    return jsonify({"ok": True})

@app.route('/api/mode', methods=['POST'])
def mode():
    d = request.get_json(silent=True) or {}
    nuevo = str(d.get("modo") or d.get("mode") or "DEMO").upper()
    config["modo"] = nuevo
    if client and config["conectado"]:
        try:
            client.change_account("demo" if nuevo=="DEMO" else "real")
            time.sleep(1)
            config["saldo"] = client.get_balance()
            config["base"] = config["saldo"]
        except Exception as e: print(e)
    return jsonify(get_data())

@app.route('/api/start', methods=['POST'])
def start(): config["activo"]=True; config["base"]=config["saldo"]; return jsonify(get_data())
@app.route('/api/stop', methods=['POST'])
def stop(): config["activo"]=False; return jsonify(get_data())
@app.route('/api/config', methods=['POST'])
def cfg():
    d = request.get_json(silent=True) or {}
    if "monto" in d: config["monto_pct"]=int(float(d["monto"]))
    if "monto_pct" in d: config["monto_pct"]=int(float(d["monto_pct"]))
    return jsonify(get_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
