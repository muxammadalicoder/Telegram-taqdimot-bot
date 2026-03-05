import os
from flask import Flask, request
import requests
from pptx import Presentation
import openai

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def send_document(chat_id, file_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": chat_id})

def generate_slides(topic):

    prompt = f"""
    {topic} haqida taqdimot uchun 8 ta slide yoz.

    format:

    Slide 1: title
    text

    Slide 2: title
    text
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}]
    )

    text = response["choices"][0]["message"]["content"]

    slides = text.split("Slide")

    result = []

    for slide in slides:
        if ":" in slide:
            parts = slide.split("\n",1)
            title = parts[0].replace(":","").strip()
            body = parts[1].strip() if len(parts)>1 else ""
            result.append((title,body))

    return result


def create_presentation(topic):

    slides = generate_slides(topic)

    prs = Presentation()

    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = topic
    title_slide.placeholders[1].text = "AI yordamida yaratilgan taqdimot"

    for title, body in slides:

        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title
        slide.placeholders[1].text = body[:700]

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

            send_message(chat_id,"Mavzuni yuboring\nMasalan: Sun'iy intellekt")

        else:

            send_message(chat_id,"🤖 AI taqdimot tayyorlamoqda...")

            file = create_presentation(text)

            send_document(chat_id,file)

    return "ok"


@app.route("/")
def home():
    return "Bot ishlayapti"


if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
