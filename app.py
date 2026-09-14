import os, threading, time, logging
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"=== BOT_TOKEN existe? {'SI' if BOT_TOKEN else 'NO'} ===")

app = Flask(__name__)
@app.route('/')
def home(): return "BOT YUYU V5 ONLINE", 200

USER_DATA = {}

def get_user(uid):
    if uid not in USER_DATA:
        USER_DATA[uid] = {"mode":"DEMO", "perc":2, "amount":1, "email":"", "pass":"", "step":None}
    return USER_DATA[uid]

def menu_text(u):
    d = get_user(u)
    return f"🤖 BOT QUOTEX V5\n\nModo: {d['mode']}\n% Gestión: {d['perc']}%\nEntrada: ${d['amount']}\nCorreo: {d['email'] or 'No puesto'}"

def menu_kb(u):
    d = get_user(u)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{'✅' if d['mode']=='DEMO' else ''} DEMO", callback_data="mode_DEMO"),
         InlineKeyboardButton(f"{'✅' if d['mode']=='REAL' else ''} REAL", callback_data="mode_REAL")],
        [InlineKeyboardButton(f"{'✅' if d['perc']==2 else ''} 2%", callback_data="perc_2"),
         InlineKeyboardButton("1%", callback_data="perc_1"),
         InlineKeyboardButton("5%", callback_data="perc_5"),
         InlineKeyboardButton("10%", callback_data="perc_10")],
        [InlineKeyboardButton(f"💰 Entrada ${d['amount']}", callback_data="set_amount")],
        [InlineKeyboardButton("📧 Correo", callback_data="set_email"),
         InlineKeyboardButton("🔑 Clave", callback_data="set_pass")],
        [InlineKeyboardButton("🔗 CONECTAR", callback_data="conectar")]
    ])

def start(update, context):
    uid = update.effective_user.id
    update.message.reply_text(menu_text(uid), reply_markup=menu_kb(uid))

def button(update, context):
    query = update.callback_query
    query.answer()
    uid = query.from_user.id
    d = get_user(uid)
    data = query.data
    if data.startswith("mode_"): d["mode"]=data.split("_")[1]
    elif data.startswith("perc_"): d["perc"]=int(data.split("_")[1])
    elif data=="set_amount": d["step"]="amount"; query.message.reply_text("Escribe el monto: ej 1 o 10"); return
    elif data=="set_email": d["step"]="email"; query.message.reply_text("Escribe tu correo Quotex:"); return
    elif data=="set_pass": d["step"]="pass"; query.message.reply_text("Escribe tu clave:"); return
    elif data=="conectar":
        if not d["email"] or not d["pass"]:
            query.message.reply_text("❌ Primero pon correo y clave"); return
        query.message.reply_text(f"✅ CONECTADO {d['mode']} - {d['email']} - {d['perc']}% - ${d['amount']}")
    try: query.edit_message_text(menu_text(uid), reply_markup=menu_kb(uid))
    except: pass

def handle_text(update, context):
    uid = update.effective_user.id
    d = get_user(uid)
    txt = update.message.text.strip()
    if d["step"]=="amount":
        try: d["amount"]=float(txt); d["step"]=None; update.message.reply_text(f"Monto puesto: ${d['amount']}", reply_markup=menu_kb(uid))
        except: update.message.reply_text("Número inválido, ej: 10")
    elif d["step"]=="email": d["email"]=txt; d["step"]=None; update.message.reply_text(f"Correo guardado: {txt}", reply_markup=menu_kb(uid))
    elif d["step"]=="pass": d["pass"]=txt; d["step"]=None; update.message.reply_text("Clave guardada ✅", reply_markup=menu_kb(uid))

def run_bot():
    if not BOT_TOKEN:
        print("ERROR CRITICO: BOT_TOKEN no encontrado en Environment!")
        return
    try:
        print("Iniciando bot... borrando webhook...")
        up = Updater(BOT_TOKEN, use_context=True)
        up.bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
        dp = up.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("menu", start))
        dp.add_handler(CallbackQueryHandler(button))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
        print("BOT INICIADO CORRECTAMENTE - /start listo")
        up.start_polling(drop_pending_updates=True)
        up.idle()
    except Exception as e:
        print(f"ERROR BOT: {e}")

threading.Thread(target=run_bot, daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
