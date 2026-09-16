import os
import threading
from flask import Flask, send_from_directory
from flask_cors import CORS
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
URL = os.environ.get("RENDER_EXTERNAL_URL", "")

app_flask = Flask(__name__, static_folder='webapp')
CORS(app_flask)

@app_flask.route('/')
def index():
    return send_from_directory('webapp', 'index.html')

@app_flask.route('/<path:path>')
def serve(path):
    return send_from_directory('webapp', path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    webapp_url = f"{URL}" if URL else "https://dashboard.render.com"
    # Si tienes tu URL de render, la usa
    keyboard = [
        [InlineKeyboardButton("📊 ABRIR PANEL YUYU", web_app=WebAppInfo(url=f"{URL}/" if URL else "https://google.com"))]
    ]
    # Si aún no tienes URL, te mando el panel directo
    if not URL:
        keyboard = [[InlineKeyboardButton("📊 ABRIR PANEL YUYU", web_app=WebAppInfo(url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'bot-quotex-telegram.onrender.com')}"))]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚀 **Quotex Bot Yuyu**\nTrading mode: DEMO\n\nDale al botón para abrir tu panel:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def run_bot():
    if not BOT_TOKEN:
        print("NO HAY BOT_TOKEN")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Bot Telegram Iniciado")
    application.run_polling()

def run_flask():
    app_flask.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()
