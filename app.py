import os, threading, asyncio
from flask import Flask, send_from_directory
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
# ESTA ES LA URL DE TU DISEÑO - DONDE SE VE EL PANEL
URL_PANEL = "https://bot-quotex-telegram-yuyu.onrender.com"

flask_app = Flask(__name__, static_folder='webapp')
@flask_app.route('/')
def index():
    return send_from_directory('webapp', 'index.html')
@flask_app.route('/<path:path>')
def serve(path):
    return send_from_directory('webapp', path)

# COMANDO /start - MANDA EL DISEÑO
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 ABRIR MI DISEÑO", web_app=WebAppInfo(url=URL_PANEL))],
        [InlineKeyboardButton("🌍 Abrir en Google", url=URL_PANEL)],
        [InlineKeyboardButton("📍 Mandar Coordenadas", callback_data="coords")]
    ]
    await update.message.reply_text(
        f"🚀 Aquí está tu diseño Yuyu:\n\n🔗 {URL_PANEL}\n\nDale al botón para abrirlo dentro de Telegram:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# COMANDO /panel - LO MISMO
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# COMANDO /coordenadas 6.2442 -75.5812 - EJEMPLO GOOGLE MAPS
async def coordenadas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Si escribes /coordenadas 6.2442 -75.5812 te manda el link de Google
    if len(context.args) == 2:
        lat = context.args[0]
        lon = context.args[1]
        google_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        keyboard = [
            [InlineKeyboardButton("🌍 Abrir en Google Maps", url=google_url)],
            [InlineKeyboardButton("📍 Abrir en Maps", url=maps_url)]
        ]
        await update.message.reply_text(
            f"📍 Coordenadas: {lat}, {lon}\n\n🔗 Google: {google_url}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "Usa así:\n/coordenadas 6.2442 -75.5812\n\nO usa /start para ver tu diseño"
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Ejemplo de coordenadas de Medellín
    lat = "6.2442"
    lon = "-75.5812"
    google_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    keyboard = [[InlineKeyboardButton("🌍 Ver en Google Maps", url=google_url)]]
    await query.message.reply_text(
        f"📍 Coordenadas de prueba:\n{lat}, {lon}\n{google_url}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def run_bot():
    try:
        print(f"BOT_TOKEN: {'SI HAY' if BOT_TOKEN else 'NO HAY'}")
        asyncio.set_event_loop(asyncio.new_event_loop())
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("panel", panel))
        app.add_handler(CommandHandler("coordenadas", coordenadas))
        from telegram.ext import CallbackQueryHandler
        app.add_handler(CallbackQueryHandler(button_callback))
        print("BOT INICIADO - Manda /start en Telegram")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"ERROR BOT: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    flask_app.run(host='0.0.0.0', port=PORT)
