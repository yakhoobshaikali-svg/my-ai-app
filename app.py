import os
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from groq import Groq

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "pdf_file" not in request.files:
        return "No file uploaded"

    file = request.files["pdf_file"]

    if file.filename == "":
        return "No selected file"

    if not file.filename.endswith(".pdf"):
        return "Please upload a PDF file"

    try:
        # Read PDF
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        if not text.strip():
            return "Could not extract text from PDF"

        # 🔥 Limit text to avoid rate limits
        text = text[:3000]

        # -------- SUMMARY --------
        summary_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this for exam preparation in clear bullet points:\n{text}"
                }
            ]
        )

        summary = summary_response.choices[0].message.content

        # -------- QUESTIONS --------
        question_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"Generate 5 important exam questions from this content:\n{text}"
                }
            ]
        )

        questions = question_response.choices[0].message.content

        return render_template(
            "result.html",
            summary=summary,
            questions=questions
        )

    except Exception as e:
        return f"Error occurred: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
