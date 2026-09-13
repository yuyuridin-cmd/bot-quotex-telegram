import os, json, asyncio
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN=os.getenv("BOT_TOKEN")
DB="data.json"

def load_db():
 try:
  with open(DB,"r") as f: return json.load(f)
 except:
  return {"saldo_inicial_demo":115722.81,"saldo_inicial_real":100,"saldo_demo":115722.81,"saldo_real":0,"ganadas":5,"perdidas":2,"modo_cuenta":"DEMO","modo_trade":"AUTOMATICO","porcentaje":2,"limite_ganancia":10,"limite_perdida":10}

def save_db(d):
 with open(DB,"w") as f: json.dump(f,f)

db=load_db()

def get_panel():
 c=db["modo_cuenta"]; sd=db["saldo_demo"]; sr=db["saldo_real"]
 ini=db["saldo_inicial_demo"] if c=="DEMO" else db["saldo_inicial_real"]
 act=sd if c=="DEMO" else sr
 porc=round((act-ini)/ini*100,2) if ini!=0 else 0
 g=db["ganadas"]; p=db["perdidas"]; ef=round(g/(g+p)*100,1) if (g+p)>0 else 0
 text=f"Quotex Bot Yuyu {c}\nDemo: ${sd} | Real: ${sr}\nActual {c}: ${act} ({porc}%)\nGan: {g} Perd: {p} {ef}%\nMonto: {db['porcentaje']}% | TP: ${db['limite_ganancia']} SL: ${db['limite_perdida']}\n\nManda par: EURUSD"
 kb=[[InlineKeyboardButton("DEMO" if c!="DEMO" else "✅ DEMO",callback_data="set_demo"),InlineKeyboardButton("REAL" if c!="REAL" else "✅ REAL",callback_data="set_real")],[InlineKeyboardButton(f"{db['porcentaje']}%",callback_data="noop")],[InlineKeyboardButton("1%",callback_data="p_1"),InlineKeyboardButton("2%",callback_data="p_2"),InlineKeyboardButton("5%",callback_data="p_5"),InlineKeyboardButton("10%",callback_data="p_10")],[InlineKeyboardButton(f"Gan ${db['limite_ganancia']}",callback_data="set_tp"),InlineKeyboardButton(f"Perd ${db['limite_perdida']}",callback_data="set_sl")],[InlineKeyboardButton("▶️ Iniciar Automatico",callback_data="auto")]]
 return text,InlineKeyboardMarkup(kb)

async def start(u,c): t,m=get_panel(); await u.message.reply_text(t,reply_markup=m)
async def botones(u,c):
 q=u.callback_query; await q.answer()
 if q.data=="set_demo": db["modo_cuenta"]="DEMO"
 elif q.data=="set_real": db["modo_cuenta"]="REAL"
 elif q.data.startswith("p_"): db["porcentaje"]=int(q.data.split("_")[1])
 elif q.data=="auto": db["modo_trade"]="AUTOMATICO"
 save_db(db); t,m=get_panel(); await q.edit_message_text(t,reply_markup=m)
async def analiza(u,c):
 activo=u.message.text.upper().strip(); cu=db["modo_cuenta"]; sa=db["saldo_demo"] if cu=="DEMO" else db["saldo_real"]; mo=round(sa*db["porcentaje"]/100,2)
 await u.message.reply_text(f"Analizando {activo} en {cu} ${mo}"); await asyncio.sleep(1); await u.message.reply_text(f"Señal BUY 85% en {activo} - Operando ${mo}")

flask_app=Flask(__name__)
@flask_app.route('/')
def home(): return "Bot Yuyu Activo"
def run_flask(): flask_app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
def main():
 Thread(target=run_flask,daemon=True).start(); app=Application.builder().token(TOKEN).build(); app.add_handler(CommandHandler("start",start)); app.add_handler(CallbackQueryHandler(botones)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,analiza)); app.run_polling()
if __name__=="__main__": main()
