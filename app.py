import os
import threading
from flask import Flask, send_from_directory
from flask_cors import CORS
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
URL = "https://bot-quotex-telegram-yuyu.onrender.com"

app_flask = Flask(__name__, static_folder='webapp')
CORS(app_flask)

@app_flask.route('/')
def index():
    return send_from_directory('webapp', 'index.html')
@app_flask.route('/<path:path>')
def serve(path):
    return send_from_directory('webapp', path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 ABRIR PANEL YUYU", web_app=WebAppInfo(url=URL))]]
    await update.message.reply_text("🚀 Bot Yuyu Activo! Dale al boton:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_bot():
    if not BOT_TOKEN:
        print("ERROR: No BOT_TOKEN")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot Yuyu iniciado correctamente")
    app.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app_flask.run(host='0.0.0.0', port=PORT)
