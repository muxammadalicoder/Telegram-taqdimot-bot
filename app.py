import os
from flask import Flask, request
import telebot
import google.generativeai as genai

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return "Bot ishlayapti"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok"

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message,"Salom! Men Gemini AI botman. Savol bering.")

@bot.message_handler(func=lambda message: True)
def ai(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message,response.text)
    except:
        bot.reply_to(message,"Xatolik yuz berdi.")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)
