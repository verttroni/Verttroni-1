import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq

# Token များကို Environment မှယူသည်
MY_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Button Layout
main_keyboard = [
    ['🖼 ပုံထုတ်ရန်', '💬 စာမေးရန်'],
    ['🔗 Link ရှာရန်', '🎥 Video ထုတ်ရန်']
]
markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Active!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ Verttroni Bot မှ ကြိုဆိုပါတယ်။",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text == '💬 စာမေးရန်':
        await update.message.reply_text("ဘာသိချင်ပါသလဲ? မေးခွန်းပို့ပေးပါ။")
        return
    elif user_text in ['🖼 ပုံထုတ်ရန်', '🔗 Link ရှာရန်', '🎥 Video ထုတ်ရန်']:
        await update.message.reply_text("ဒီ Feature က မကြာခင် လာပါတော့မယ်။")
        return
    
    try:
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
        )
        await update.message.reply_text(chat_completion.choices[0].message.content, reply_markup=markup)
    except Exception as e:
        print(f"Error: {e}")

threading.Thread(target=run_health_check, daemon=True).start()
app = ApplicationBuilder().token(MY_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
