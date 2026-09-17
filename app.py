import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

config = {
    "email": "", "password": "", "monto": 1, "porcentaje": 2,
    "limite_gana": 50, "limite_pierde": 20,
    "base": 0, "balance_actual": 1000, "activo": False,
    "wins": 0, "loss": 0, "esperando": None, "modo": "DEMO", "operacion": "AUTO", "chat_id": None
}

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "BOT YUYU V4 ACTIVO", 200

async def send_menu(context):
    if config['chat_id'] is None: return
    calc = round(config['balance_actual'] * config['porcentaje']/100, 2)
    if config.get('usando_porcentaje', True):
        config['monto'] = calc
    total = config['wins']+config['loss']
    efect = round((config['wins']/total*100) if total>0 else 0)
    ganancia_actual = config['balance_actual'] - config['base'] if config['base']>0 else 0

    txt = f"🤖 *BOT V4 YUYU* - {'🟢 CORRIENDO' if config['activo'] else '⏸️ DETENIDO'}\n\nCuenta: {config['modo']}\n💰 Saldo: ${config['balance_actual']:.2f} ({ganancia_actual:+.2f} desde base)\n📊 {config['wins']}W-{config['loss']}L | {efect}%\n\n*Monto:* ${config['monto']} / {config['porcentaje']}%\n🎯 Ganancia: +${config['limite_gana']} | 🛑 Pérdida: -${config['limite_pierde']}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{'✅ ' if config['modo']=='DEMO' else ''}DEMO", callback_data="modo_demo"), InlineKeyboardButton(f"{'✅ ' if config['modo']=='REAL' else ''}REAL", callback_data="modo_real")],
        [InlineKeyboardButton(f"2%{' ✅' if config['porcentaje']==2 else ''}", callback_data="pct_2"), InlineKeyboardButton(f"1%{' ✅' if config['porcentaje']==1 else ''}", callback_data="pct_1"), InlineKeyboardButton(f"5%{' ✅' if config['porcentaje']==5 else ''}", callback_data="pct_5"), InlineKeyboardButton(f"10%{' ✅' if config['porcentaje']==10 else ''}", callback_data="pct_10")],
        [InlineKeyboardButton(f"💰 Entrada ${config['monto']} (Tocar para cambiar)", callback_data="set_monto")],
        [InlineKeyboardButton(f"🎯 Ganancia +${config['limite_gana']}", callback_data="set_gana"), InlineKeyboardButton(f"🛑 Pérdida -${config['limite_pierde']}", callback_data="set_pierde")],
        [InlineKeyboardButton(f"{'✅ ' if config['operacion']=='AUTO' else ''}🤖 Automático", callback_data="op_auto"), InlineKeyboardButton(f"{'✅ ' if config['operacion']=='MANUAL' else ''}👆 Manual", callback_data="op_manual")],
        [InlineKeyboardButton("🚀 INICIAR BOT", callback_data="start_bot"), InlineKeyboardButton("🛑 PARAR", callback_data="stop")],
    ])
    try:
        await context.bot.send_message(chat_id=config['chat_id'], text=txt, parse_mode="Markdown", reply_markup=kb)
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config['chat_id'] = update.effective_chat.id
    if config['base']==0: config['base']=config['balance_actual']
    await send_menu(context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config['chat_id']=update.effective_chat.id
    msg=update.message.text.strip()
    if config['esperando']=="monto" and msg.replace('.','',1).isdigit():
        config['monto']=float(msg); config['usando_porcentaje']=False; config['esperando']=None
        await update.message.reply_text(f"✅ Monto fijo: ${msg} - Tú lo decidiste")
        await send_menu(context); return
    if config['esperando']=="gana" and msg.replace('.','',1).isdigit():
        config['limite_gana']=float(msg); config['esperando']=None; await send_menu(context); return
    if config['esperando']=="pierde" and msg.replace('.','',1).isdigit():
        config['limite_pierde']=float(msg); config['esperando']=None; await send_menu(context); return
    if msg.replace('.','',1).isdigit():
        config['monto']=float(msg); config['usando_porcentaje']=False
        await update.message.reply_text(f"✅ Monto puesto: ${msg}")
        await send_menu(context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); d=q.data; config['chat_id']=update.effective_chat.id
    if d.startswith("pct_"):
        p=int(d.split("_")[1]); config['porcentaje']=p; config['usando_porcentaje']=True
        config['monto']=round(config['balance_actual']*p/100,2)
        await send_menu(context)
    elif d=="set_monto":
        config['esperando']="monto"; await context.bot.send_message(chat_id=config['chat_id'], text="✏️ Escribe la cantidad que TU quieras:\nEj: 1 o 10")
    elif d=="set_gana":
        config['esperando']="gana"; await context.bot.send_message(chat_id=config['chat_id'], text="✏️ Límite ganancia Ej: 50")
    elif d=="set_pierde":
        config['esperando']="pierde"; await context.bot.send_message(chat_id=config['chat_id'], text="✏️ Límite pérdida Ej: 20")
    elif d=="modo_demo": config['modo']="DEMO"; await send_menu(context)
    elif d=="modo_real": config['modo']="REAL"; await send_menu(context)
    elif d=="op_auto": config['operacion']="AUTO"; await send_menu(context)
    elif d=="op_manual": config['operacion']="MANUAL"; await send_menu(context)
    elif d=="start_bot":
        config['activo']=True; config['base']=config['balance_actual']
        await send_menu(context)
    elif d=="stop": config['activo']=False; await send_menu(context)

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot Yuyu V4 iniciado correctamente - Sin error Updater")
    app.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    flask_app.run(host='0.0.0.0', port=PORT)
