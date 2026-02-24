import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq

# --- Token နဲ့ Key တွေကို ဒီမှာ ထည့်ပေးထားပါတယ် ---
MY_BOT_TOKEN = "8730139251:AAFohZgxYIKTVCNlpA4r_Kk2UTc4nmhyxYs"
GROQ_API_KEY = "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"
# -------------------------------------------

client = Groq(api_key=GROQ_API_KEY)

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
    await update.message.reply_text("မင်္ဂလာပါ၊ Verttroni Bot မှ ကြိုဆိုပါတယ်။ ဘာသိချင်ပါသလဲ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
        )
        await update.message.reply_text(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")

# Render အတွက် Health Check Server ကို background မှာပတ်ထားမယ်
threading.Thread(target=run_health_check, daemon=True).start()

# Telegram Bot ကို စတင်ခြင်း
app = ApplicationBuilder().token(MY_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

print("Bot is starting...")
app.run_polling()
