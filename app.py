import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot Yuyu Running!"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola Yuyu! Bot activo ✅ Escribe /help")

def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Comandos: /start /help")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    import threading
    threading.Thread(target=main).start()
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
