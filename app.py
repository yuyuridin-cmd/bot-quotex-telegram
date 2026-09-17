import os, threading, time, traceback, asyncio
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Import
Quotex = None
IMPORT_ERROR = ""
try:
    from quotexapi.stable_api import Quotex
except Exception as e:
    IMPORT_ERROR = str(e)
    try:
        from pyquotex.stable_api import Quotex
    except Exception as e2:
        IMPORT_ERROR += " | " + str(e2)

HAS_QUOTEX = Quotex is not None
PORT = 10000

config = {
    "saldo": 0, "base": 0, "wins": 0, "loss": 0,
    "monto_pct": 6, "limite_gana": 10, "limite_perdida": 10,
    "modo": "DEMO", "activo": False, "conectado": False,
    "email": "", "msg": ""
}
client = None

def get_data():
    base = config["base"] or config["saldo"] or 1
    gan = config["saldo"] - base
    porc = round((gan / base * 100) if base>0 else 0, 2)
    total = config["wins"]+config["loss"]
    efect = int((config["wins"]/total*100)) if total>0 else 0
    return {
        "saldo": config["saldo"], "balance": config["saldo"],
        "base": config["base"], "ganancia": gan,
        "porcentaje_hoy": porc, "porcentaje": porc,
        "wins": config["wins"], "loss": config["loss"],
        "efectividad": efect, "monto_pct": config["monto_pct"],
        "monto": config["monto_pct"], "modo": config["modo"],
        "conectado": config["conectado"], "email": config["email"],
        "activo": config["activo"], "msg": config["msg"]
    }

def loop_saldo():
    while True:
        try:
            if client and config["conectado"]:
                try:
                    # balance puede ser async o sync
                    bal = client.get_balance()
                    if asyncio.iscoroutine(bal):
                        bal = asyncio.run(bal)
                    if bal is not None:
                        config["saldo"] = bal
                except: pass
                
                if config["activo"]:
                    gan = config["saldo"] - config["base"]
                    if gan >= config["limite_gana"]:
                        config["activo"]=False
                        config["msg"]=f"Meta +${gan:.2f} alcanzada"
                    if gan <= -config["limite_perdida"]:
                        config["activo"]=False
                        config["msg"]=f"Stop loss ${gan:.2f}"
        except: pass
        time.sleep(3)

app = Flask(__name__, static_folder='webapp')
CORS(app)

@app.route('/')
def index(): return send_from_directory('webapp','index.html')
@app.route('/<path:path>')
def files(path):
    if path.startswith('api/'): return jsonify(get_data())
    return send_from_directory('webapp',path)
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

        if not HAS_QUOTEX:
            return jsonify({"ok":False,"error":f"Libreria no instalada: {IMPORT_ERROR}"})

        async def do_connect():
            q = Quotex(email=email, password=password)
            check, reason = await q.connect()
            return q, check, reason

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            q_client, check, reason = loop.run_until_complete(do_connect())
        except Exception as e:
            return jsonify({"ok":False,"error":f"Error connect: {e}"})

        if not check:
            return jsonify({"ok":False,"error":f"No conecta Quotex: {reason}"})

        # cambiar a real/demo
        try:
            is_demo = 0 if modo=="REAL" else 1
            # versiones nuevas usan change_account async tambien
            res = q_client.change_account("real" if modo=="REAL" else "demo")
            if asyncio.iscoroutine(res):
                loop.run_until_complete(res)
        except: pass

        time.sleep(1)
        try:
            b = q_client.get_balance()
            if asyncio.iscoroutine(b):
                b = loop.run_until_complete(b)
            saldo = b
        except:
            saldo = 0

        client = q_client
        config["saldo"]=saldo
        config["base"]=saldo
        config["conectado"]=True
        config["email"]=email
        config["modo"]=modo
        config["msg"]="Conectado"
        
        threading.Thread(target=loop_saldo, daemon=True).start()
        return jsonify({"ok":True, **get_data()})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok":False,"error": str(e)})

@app.route('/api/logout', methods=['POST'])
def logout():
    global client
    config["conectado"]=False; config["email"]=""; config["saldo"]=0; config["activo"]=False; client=None
    return jsonify({"ok":True})

@app.route('/api/mode', methods=['POST'])
def mode():
    d=request.get_json(silent=True) or {}
    nuevo=str(d.get("modo") or "DEMO").upper()
    config["modo"]=nuevo
    return jsonify(get_data())

@app.route('/api/start', methods=['POST'])
def start():
    config["activo"]=True
    config["base"]=config["saldo"]
    config["msg"]="Bot activo"
    return jsonify(get_data())

@app.route('/api/stop', methods=['POST'])
def stop():
    config["activo"]=False
    config["msg"]="Bot parado"
    return jsonify(get_data())

@app.route('/api/config', methods=['POST'])
def cfg():
    d=request.get_json(silent=True) or {}
    if "monto" in d: config["monto_pct"]=int(float(d["monto"]))
    if "monto_pct" in d: config["monto_pct"]=int(float(d["monto_pct"]))
    return jsonify(get_data())

if __name__=='__main__':
    app.run(host='0.0.0.0', port=PORT)
