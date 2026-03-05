import os
from flask import Flask, request
import requests
from pptx import Presentation
from pptx.util import Inches

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def send_document(chat_id, file_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": chat_id})

def create_presentation(topic):
    prs = Presentation()

    # Title slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = topic
    slide.placeholders[1].text = "Telegram orqali yaratilgan taqdimot"

    # Content slide
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Kirish"
    slide.placeholders[1].text = f"{topic} haqida umumiy ma'lumot"

    file_path = "presentation.pptx"
    prs.save(file_path)
    return file_path

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.json

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Mavzuni yuboring. Masalan: Sun’iy intellekt")

        else:
            send_message(chat_id, "Taqdimot tayyorlanmoqda...")
            file_path = create_presentation(text)
            send_document(chat_id, file_path)

    return "ok"

@app.route("/")
def home():
    return "Bot ishlayapti 🚀"

if __name__ == "__main__":
    app.run()
