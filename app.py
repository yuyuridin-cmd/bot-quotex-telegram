import os, threading, asyncio, time, random, traceback
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
URL_PANEL = "https://bot-quotex-telegram-yuyu.onrender.com"

# TU CONFIGURACION REAL
config = {
    "saldo": 115722.81, "base": 115722.81, "wins": 0, "loss": 0,
    "monto_pct": 6, "limite_gana": 10, "limite_perdida": 10,
    "modo": "DEMO", "activo": False, "chat_id": None
}

flask_app = Flask(__name__, static_folder='webapp')
CORS(flask_app)

# --- RUTAS PARA GOOGLE (TU DISEÑO) ---
@flask_app.route('/')
def index(): return send_from_directory('webapp', 'index.html')
@flask_app.route('/<path:path>')
def serve(path): return send_from_directory('webapp', path)

@flask_app.route('/api/status')
def status():
    ganancia = config["saldo"] - config["base"]
    total = config["wins"]+config["loss"]
    efect = round((config["wins"]/total*100) if total>0 else 0)
    return jsonify({
        "saldo": config["saldo"], "base": config["base"], "ganancia": ganancia,
        "wins": config["wins"], "loss": config["loss"], "efectividad": efect,
        "monto_pct": config["monto_pct"], "limite_gana": config["limite_gana"],
        "limite_perdida": config["limite_perdida"], "modo": config["modo"], "activo": config["activo"]
    })

@flask_app.route('/api/start', methods=['POST'])
def api_start():
    config["activo"] = True
    config["base"] = config["saldo"]
    return jsonify({"ok": True, "msg": "Bot iniciado"})

@flask_app.route('/api/stop', methods=['POST'])
def api_stop():
    config["activo"] = False
    return jsonify({"ok": True, "msg": "Bot parado"})

@flask_app.route('/api/config', methods=['POST'])
def api_config():
    data = request.json
    if "monto_pct" in data: config["monto_pct"] = int(data["monto_pct"])
    if "limite_gana" in data: config["limite_gana"] = float(data["limite_gana"])
    if "limite_perdida" in data: config["limite_perdida"] = float(data["limite_perdida"])
    if "modo" in data: config["modo"] = data["modo"]
    return jsonify({"ok": True})

# --- BOT PARA TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config["chat_id"] = update.effective_chat.id
    kb = [
        [InlineKeyboardButton("📊 ABRIR PANEL (Tu Diseño)", web_app=WebAppInfo(url=URL_PANEL))],
        [InlineKeyboardButton("🚀 INICIAR AUTOMATICO", callback_data="iniciar")],
        [InlineKeyboardButton("🛑 PARAR", callback_data="parar")]
    ]
    txt = f"💰 Saldo: ${config['saldo']:.2f} | {config['modo']}\n📊 {config['wins']}W - {config['loss']}L\nMonto: {config['monto_pct']}% | Limites: +${config['limite_gana']} / -${config['limite_perdida']}\n\nEstado: {'🟢 CORRIENDO' if config['activo'] else '🔴 DETENIDO'}\n\nDale a ABRIR PANEL para ver el diseño de la foto:"
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    config["chat_id"] = update.effective_chat.id
    if q.data == "iniciar":
        config["activo"] = True
        config["base"] = config["saldo"]
        await q.message.reply_text("✅ Bot INICIADO desde Telegram. Revisa Google, ya debe decir CORRIENDO.")
    elif q.data == "parar":
        config["activo"] = False
        await q.message.reply_text("🛑 Bot PARADO desde Telegram.")

def trading_loop():
    while True:
        try:
            if config["activo"]:
                # AQUI VA TU LOGICA REAL DE QUOTEX
                # Por ahora simula una operacion cada 20 seg
                time.sleep(20)
                gano = random.choice([True, False])
                monto = config["saldo"] * (config["monto_pct"]/100)
                if gano:
                    config["saldo"] += monto*0.8
                    config["wins"] += 1
                else:
                    config["saldo"] -= monto
                    config["loss"] += 1
                
                ganancia_hoy = config["saldo"] - config["base"]
                # Revisa limites
                if ganancia_hoy >= config["limite_gana"] or ganancia_hoy <= -config["limite_perdida"]:
                    config["activo"] = False
                    print(f"LIMITE ALCANZADO: {ganancia_hoy}")
            else:
                time.sleep(2)
        except Exception as e:
            print(f"Error loop: {e}"); time.sleep(5)

def run_bot():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("panel", start))
        from telegram.ext import CallbackQueryHandler
        app.add_handler(CallbackQueryHandler(button_handler))
        print("BOT TELEGRAM INICIADO OK")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"ERROR BOT: {e}"); traceback.print_exc()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=trading_loop, daemon=True).start()
    flask_app.run(host='0.0.0.0', 
