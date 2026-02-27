from flask import Flask, render_template, request
import google.generativeai as genai
import os
import PyPDF2
import io

app = Flask(__name__)

# Configure API Key (Render Environment Variable)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Stable working model
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET", "POST"])
def home():
    summary = None
    questions = None

    if request.method == "POST":
        try:
            uploaded_file = request.files["file"]

            if not uploaded_file:
                summary = "No file uploaded."
                return render_template("index.html", summary=summary)

            if not uploaded_file.filename.endswith(".pdf"):
                summary = "Please upload a PDF file."
                return render_template("index.html", summary=summary)

            # Read PDF properly
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""

            for page in pdf_reader.pages:
                content = page.extract_text()
                if content:
                    text += content

            if not text.strip():
                summary = "Unable to extract text from this PDF."
                return render_template("index.html", summary=summary)

            # Generate Summary
            summary_response = model.generate_content(
                f"Summarize this for exam preparation:\n{text}"
            )

            summary = summary_response.text

            # Generate Questions
            question_response = model.generate_content(
                f"Generate 5 important exam questions from this:\n{text}"
            )

            questions = question_response.text.split("\n")

        except Exception as e:
            summary = f"AI Error: {str(e)}"

    return render_template("index.html",
                           summary=summary,
                           questions=questions)

if __name__ == "__main__":
    app.run()
