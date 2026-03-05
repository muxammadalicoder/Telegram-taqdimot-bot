import os
from flask import Flask, request
import telebot
import google.generativeai as genai

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")

        response = model.generate_content(message.text)

        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "Javob topilmadi")

    except Exception as e:
        print(e)
        bot.reply_to(message, "Xatolik yuz berdi")


@app.route("/", methods=["GET"])
def home():
    return "Bot ishlayapti"


@app.route("/", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
