import os
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    summary = None
    questions = None
    error = None

    if "pdf_file" not in request.files:
        error = "No file uploaded"
    else:
        file = request.files["pdf_file"]

        if file.filename == "":
            error = "No file selected"
        elif not file.filename.endswith(".pdf"):
            error = "Please upload a PDF file"
        else:
            try:
                reader = PdfReader(file)
                text = ""

                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted

                text = text[:3000]

                summary_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "user",
                            "content": f"Summarize this for exam preparation in bullet points:\n{text}"
                        }
                    ]
                )

                summary = summary_response.choices[0].message.content

                question_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "user",
                            "content": f"Generate 5 important exam questions:\n{text}"
                        }
                    ]
                )

                questions = question_response.choices[0].message.content

            except Exception as e:
                error = f"Error occurred: {str(e)}"

    return render_template(
        "index.html",
        summary=summary,
        questions=questions,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
