from flask import Flask, render_template, request
from google import genai
import os
import PyPDF2
import io

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    summary = None
    questions = None

    if request.method == "POST":
        try:
            uploaded_file = request.files.get("file")

            if not uploaded_file:
                summary = "No file uploaded."
                return render_template("index.html", summary=summary)

            if not uploaded_file.filename.endswith(".pdf"):
                summary = "Please upload a PDF file only."
                return render_template("index.html", summary=summary)

            # ✅ Read PDF properly
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""

            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            if not text.strip():
                summary = "Could not extract text from this PDF."
                return render_template("index.html", summary=summary)

            # 🔥 Gemini API Call
            response_summary = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Summarize clearly for exam preparation:\n{text}"
            )

            response_questions = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Generate 5 important exam questions:\n{text}"
            )

            summary = response_summary.text
            questions = response_questions.text.split("\n")

        except Exception as e:
            summary = f"AI Error: {str(e)}"

    return render_template("index.html",
                           summary=summary,
                           questions=questions)

if __name__ == "__main__":
    app.run()
