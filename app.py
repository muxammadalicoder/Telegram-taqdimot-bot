import os
import requests
from flask import Flask, request
from pptx import Presentation
from fpdf import FPDF

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def send_document(chat_id, file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": chat_id})

def ask_gemini(prompt):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    data = {
        "contents":[
            {
                "parts":[
                    {"text": prompt}
                ]
            }
        ]
    }

    r = requests.post(url, json=data)

    result = r.json()

    return result["candidates"][0]["content"]["parts"][0]["text"]

def create_ppt(topic):

    text = ask_gemini(f"{topic} haqida taqdimot uchun 10 ta qisqa punkt yoz")

    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = topic
    slide.placeholders[1].text = "AI yaratgan taqdimot"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Ma'lumot"
    slide.placeholders[1].text = text

    file = "presentation.pptx"
    prs.save(file)

    return file

def create_pdf(topic):

    text = ask_gemini(f"{topic} haqida referat yoz")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.cell(0,10,line,ln=True)

    file = "referat.pdf"
    pdf.output(file)

    return file


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():

    update = request.json

    if "message" in update:

        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text")

        if text == "/start":

            send_message(chat_id,
            "🤖 SUPER GEMINI AI BOT\n\n"
            "Buyruqlar:\n"
            "/ai savol\n"
            "/ppt mavzu\n"
            "/referat mavzu")

        elif text.startswith("/ai"):

            q = text.replace("/ai","")

            answer = ask_gemini(q)

            send_message(chat_id, answer)

        elif text.startswith("/ppt"):

            topic = text.replace("/ppt","")

            send_message(chat_id,"📊 Taqdimot tayyorlanmoqda...")

            file = create_ppt(topic)

            send_document(chat_id,file)

        elif text.startswith("/referat"):

            topic = text.replace("/referat","")

            send_message(chat_id,"📄 Referat tayyorlanmoqda...")

            file = create_pdf(topic)

            send_document(chat_id,file)

        else:

            answer = ask_gemini(text)

            send_message(chat_id,answer)

    return "ok"

@app.route("/")
def home():
    return "Gemini AI bot ishlayapti 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
