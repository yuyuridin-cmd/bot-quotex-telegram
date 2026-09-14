import os, time, random, threading
from flask import Flask
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
config = {
    "email": "", "password": "", "monto": 1, "porcentaje": 2,
    "limite_gana": 50, "limite_pierde": 20,
    "base": 0, "balance_actual": 1000, "activo": False,
    "wins": 7, "loss": 3, "esperando": None, "modo": "DEMO", "operacion": "AUTO", "qx": None, "chat_id": None
}

app = Flask(__name__)
@app.route('/')
def home(): return "BOT V4 YUYU LISTO", 200

def send_menu(context):
    if config['balance_actual']>0 and config['porcentaje']>0:
        monto_calc = round(config['balance_actual'] * config['porcentaje']/100, 2)
        # Si el usuario puso monto fijo manual, usamos ese. Si puso %, usamos calculado
        if config.get('usando_porcentaje', True):
            config['monto'] = monto_calc
    
    efectividad = round((config['wins']/(config['wins']+config['loss'])*100) if (config['wins']+config['loss'])>0 else 0)
    txt=f"🤖 *BOT V4 YUYU* - {'🟢 CORRIENDO' if config['activo'] else '⏸️ DETENIDO'}\n\nCuenta: {config['modo']}\n💰 Saldo: ${config['balance_actual']:.2f}\n📊 {config['wins']}W-{config['loss']}L | {efectividad}%\n\n*Monto / Porcentaje de Entrada*\nMonto por Operación: ${config['monto']} / {config['porcentaje']}%\nEntrada actual: ${config['monto']} ≈ {config['porcentaje']}% del saldo {config['modo'].lower()}\n\nGanancia: +${config['limite_gana']} | Pérdida: -${config['limite_pierde']}"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{'✅ ' if config['modo']=='DEMO' else ''}DEMO", callback_data="modo_demo"), InlineKeyboardButton(f"{'✅ ' if config['modo']=='REAL' else ''}REAL", callback_data="modo_real")],
        [InlineKeyboardButton(f"2%{' ✅' if config['porcentaje']==2 else ''}", callback_data="pct_2"), InlineKeyboardButton(f"1%{' ✅' if config['porcentaje']==1 else ''}", callback_data="pct_1"), InlineKeyboardButton(f"5%{' ✅' if config['porcentaje']==5 else ''}", callback_data="pct_5"), InlineKeyboardButton(f"10%{' ✅' if config['porcentaje']==10 else ''}", callback_data="pct_10")],
        [InlineKeyboardButton(f"💰 Entrada ${config['monto']} (Tocar para cambiar)", callback_data="set_monto")],
        [InlineKeyboardButton(f"🎯 Ganancia +${config['limite_gana']}", callback_data="set_gana"), InlineKeyboardButton(f"🛑 Pérdida -${config['limite_pierde']}", callback_data="set_pierde")],
        [InlineKeyboardButton(f"{'✅ ' if config['operacion']=='AUTO' else ''}🤖 Automático", callback_data="op_auto"), InlineKeyboardButton(f"{'✅ ' if config['operacion']=='MANUAL' else ''}👆 Manual", callback_data="op_manual")],
        [InlineKeyboardButton("🚀 INICIAR BOT", callback_data="start"), InlineKeyboardButton("🛑 PARAR", callback_data="stop")],
        [InlineKeyboardButton("📧 Poner Correo", callback_data="set_email"), InlineKeyboardButton("🔑 Poner Clave", callback_data="set_pass")],
        [InlineKeyboardButton("🔗 CONECTAR", callback_data="conectar"), InlineKeyboardButton("🔄 Menu", callback_data="menu")],
    ])
    context.bot.send_message(chat_id=config['chat_id'], text=txt, parse_mode="Markdown", reply_markup=kb)

def conectar_quotex(context):
    try:
        from quotexapi.stable_api import Quotex
        qx=Quotex(config['email'], config['password'])
        ok,why=qx.connect()
        if ok:
            qx.change_account("demo" if config['modo']=="DEMO" else "real")
            config['qx']=qx; config['balance_actual']=qx.get_balance(); config['base']=config['balance_actual']
            context.bot.send_message(chat_id=config['chat_id'], text=f"✅ CONECTADO {config['modo']} ${config['balance_actual']:.2f}")
            send_menu(context)
        else: context.bot.send_message(chat_id=config['chat_id'], text=f"❌ {why}")
    except Exception as e: context.bot.send_message(chat_id=config['chat_id'], text=f"⚠️ {e}")

def start(update, context):
    config['chat_id']=update.effective_chat.id
    send_menu(context)

def handle_text(update, context):
    config['chat_id']=update.effective_chat.id
    msg=update.message.text.strip()
    if config['esperando']=="email" and "@" in msg:
        config['email']=msg; config['esperando']="pass"; update.message.reply_text(f"✅ Correo {msg}\nAhora escribe tu CLAVE:"); return
    if config['esperando']=="pass":
        config['password']=msg; config['esperando']=None; update.message.reply_text("Clave guardada, conectando..."); threading.Thread(target=conectar_quotex, args=(context,), daemon=True).start(); return
    if config['esperando']=="monto" and msg.replace('.','',1).isdigit():
        config['monto']=float(msg); config['usando_porcentaje']=False; config['esperando']=None; update.message.reply_text(f"✅ Monto fijo: ${msg} - Tú lo decidiste"); send_menu(context); return
    if config['esperando']=="gana" and msg.replace('.','',1).isdigit():
        config['limite_gana']=float(msg); config['esperando']=None; send_menu(context); return
    if config['esperando']=="pierde" and msg.replace('.','',1).isdigit():
        config['limite_pierde']=float(msg); config['esperando']=None; send_menu(context); return
    if "@" in msg: config['email']=msg; config['esperando']="pass"; update.message.reply_text("Correo recibido, ahora clave:"); return
    # Si escribe un numero suelto, lo toma como monto
    if msg.replace('.','',1).isdigit():
        config['monto']=float(msg); config['usando_porcentaje']=False; update.message.reply_text(f"✅ Monto puesto: ${msg}"); send_menu(context)

def button(update, context):
    q=update.callback_query; q.answer(); d=q.data; config['chat_id']=update.effective_chat.id
    if d.startswith("pct_"): 
        p=int(d.split("_")[1]); config['porcentaje']=p; config['usando_porcentaje']=True
        if config['balance_actual']>0: config['monto']=round(config['balance_actual']*p/100,2)
        send_menu(context)
    elif d=="set_monto": config['esperando']="monto"; context.bot.send_message(chat_id=config['chat_id'], text="✏️ Escribe la cantidad que TU quieras:\nEj: 1 o 10 o 50\n(Para fijo)")
    elif d=="set_gana": config['esperando']="gana"; context.bot.send_message(chat_id=config['chat_id'], text="✏️ Ganancia limite Ej: 50")
    elif d=="set_pierde": config['esperando']="pierde"; context.bot.send_message(chat_id=config['chat_id'], text="✏️ Perdida limite Ej: 20")
    elif d=="set_email": config['esperando']="email"; context.bot.send_message(chat_id=config['chat_id'], text="📧 Escribe tu correo:")
    elif d=="set_pass": config['esperando']="pass"; context.bot.send_message(chat_id=config['chat_id'], text="🔑 Escribe tu clave:")
    elif d=="conectar": threading.Thread(target=conectar_quotex, args=(context,), daemon=True).start()
    elif d=="modo_demo": config['modo']="DEMO"; send_menu(context)
    elif d=="modo_real": config['modo']="REAL"; send_menu(context)
    elif d=="op_auto": config['operacion']="AUTO"; send_menu(context)
    elif d=="op_manual": config['operacion']="MANUAL"; send_menu(context)
    elif d=="start": 
        if not config['qx']: context.bot.send_message(chat_id=config['chat_id'], text="❌ Conecta primero"); return
        config['activo']=True; config['base']=config['balance_actual']; send_menu(context)
    elif d=="stop": config['activo']=False; send_menu(context)
    elif d=="menu": send_menu(context)

def run_bot():
    updater=Updater(BOT_TOKEN, use_context=True)
    updater.bot.delete_webhook(drop_pending_updates=True)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", start))
    dp.add_handler(CallbackQueryHandler(button))
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    updater.start_polling(drop_pending_updates=True, clean=True)
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", 
