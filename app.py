import os
from flask import Flask, request
import requests
from pptx import Presentation

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def send_document(chat_id, file_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": chat_id})

def create_presentation(topic):
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = topic
    slide.placeholders[1].text = "Telegram bot yaratgan taqdimot"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Kirish"
    slide.placeholders[1].text = topic + " haqida ma'lumot"

    file = "presentation.pptx"
    prs.save(file)
    return file

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.json

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text")

        if text == "/start":
            send_message(chat_id, "Mavzuni yuboring")

        else:
            send_message(chat_id, "Taqdimot tayyorlanmoqda...")
            file = create_presentation(text)
            send_document(chat_id, file)

    return "ok"

@app.route("/")
def home():
    return "Bot ishlayapti"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
