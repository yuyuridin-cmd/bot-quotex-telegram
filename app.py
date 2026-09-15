import os, json, time, random
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from threading import Thread

TOKEN = os.getenv("TELEGRAM_TOKEN")
EMAIL = os.getenv("QUOTEX_EMAIL")
PASSWORD = os.getenv("QUOTEX_PASSWORD")

app = Flask(__name__, static_folder="webapp")
CORS(app)

DATA_FILE = "bot_data.json"
def load():
    try: return json.load(open(DATA_FILE))
    except: return {"base":0,"profit":0,"wins":0,"losses":0,"history":[],"running":False,"limits":{"gain":10,"loss":10},"mode":"DEMO","balance_demo":115722.81,"balance_real":0}
def save(d): 
    with open(DATA_FILE,"w") as f: json.dump(d,f)
data = load()

def trading_loop():
    while True:
        if data["running"]:
            current = data["balance_demo"] if data["mode"]=="DEMO" else data["balance_real"]
            profit_today = current - data["base"]
            data["profit"] = round(profit_today, 2)

            # TU LOGICA DE BASE QUE PEDISTE
            if profit_today >= data["limits"]["gain"]:
                data["running"]=False
                data["history"].append({"result":"🎯 META GANANCIA","par":"","amount":profit_today,"balance":current})
                save(data)
                print(f" META ALCANZADA {profit_today} - BOT DETENIDO")
                time.sleep(2)
                continue

            if profit_today <= -abs(data["limits"]["loss"]):
                data["running"]=False
                data["history"].append({"result":"🛑 STOP PERDIDA","par":"","amount":profit_today,"balance":current})
                save(data)
                print(f" STOP LOSS {profit_today} - BOT DETENIDO")
                time.sleep(2)
                continue

            # SIMULACION DE OPERACION (aqui es donde va q.buy() real)
            time.sleep(20) # opera cada 20 seg
            if not data["running"]: continue
            
            win = random.choice([True, True, False]) # 66% win para prueba
            amount = round(random.uniform(0.85, 1.95),2) if win else -1.0
            current += amount
            
            if data["mode"]=="DEMO": data["balance_demo"]=round(current,2)
            else: data["balance_real"]=round(current,2)

            if win: data["wins"]+=1
            else: data["losses"]+=1

            # AQUI SE SUMA O SE RESTA DE UNA A TU CUENTA COMO QUERIAS
            data["history"].append({
                "result":"✅ WIN" if win else "❌ LOSS",
                "par":"EUR/USD",
                "amount":amount,
                "balance":round(current,2)
            })
            save(data)
            print(f" {data['history'][-1]['result']} {amount} -> Saldo {current} | Ganadas:{data['wins']} Perdidas:{data['losses']}")
        else:
            time.sleep(1)

@app.route("/")
def index(): return send_from_directory("webapp","index.html")

@app.route("/api/balance")
def bal(): return jsonify({"demo":data["balance_demo"],"real":data["balance_real"],"mode":data["mode"]})

@app.route("/api/stats")
def stats():
    total=data["wins"]+data["losses"]
    eff=round(data["wins"]/total*100,1) if total>0 else 0
    return jsonify({"wins":data["wins"],"losses":data["losses"],"eff":eff,"base":data["base"],"profit_today":data["profit"],"limits":data["limits"],"history":data["history"][-20:][::-1],"running":data["running"]})

@app.route("/api/config", methods=["POST"])
def cfg():
    j=request.json
    data["limits"]["gain"]=float(j.get("gain",10))
    data["limits"]["loss"]=float(j.get("loss",10))
    data["mode"]=j.get("mode","DEMO")
    save(data)
    return jsonify({"ok":True})

@app.route("/api/start", methods=["POST"])
def start_api():
    bal_actual = data["balance_demo"] if data["mode"]=="DEMO" else data["balance_real"]
    data["base"]=bal_actual # BASE AUTOMATICA DE TU CUENTA
    data["profit"]=0
    data["wins"]=0
    data["losses"]=0
    data["history"]=[]
    data["running"]=True
    save(data)
    print(f" BOT INICIADO - MODO {data['mode']} - BASE HOY ${bal_actual}")
    return jsonify({"ok":True,"base":bal_actual})

@app.route("/api/stop", methods=["POST"])
def stop_api():
    data["running"]=False
    save(data)
    print(" BOT DETENIDO MANUAL")
    return jsonify({"ok":True})

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url=os.getenv("RENDER_EXTERNAL_URL")
    kb=[[InlineKeyboardButton("🚀 ABRIR PANEL V5 PRO", web_app=WebAppInfo(url=url))]]
    await update.message.reply_text(f"V5 PRO ACTIVO ✅\nModo: {data['mode']}\nSaldo Demo: ${data['balance_demo']}\nToca el boton:", reply_markup=InlineKeyboardMarkup(kb))

def run_tg():
    tg_app=Application.builder().token(TOKEN).build()
    tg_app.add_handler(CommandHandler("start", cmd_start))
    tg_app.run_polling()

# Render ejecuta esto
if __name__ != "__main__":
    Thread(target=trading_loop, daemon=True).start()
    Thread(target=run_tg, daemon=True).start()

if __name__=="__main__":
    Thread(target=trading_loop, daemon=True).start()
    Thread(target=run_tg, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
