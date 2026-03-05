import os
import telebot
import google.generativeai as genai
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti"

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@bot.message_handler(func=lambda message: True)
def message(message):
    user_text = message.text

    try:
        response = model.generate_content(user_text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Xatolik yuz berdi")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://telegram-taqdimot-bot.onrender.com/webhook")
    app.run(host="0.0.0.0", port=10000)
