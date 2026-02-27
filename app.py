import os
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from groq import Groq

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():

    summary = None
    questions = None
    error = None

    if request.method == "POST":

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

                    if not text.strip():
                        error = "Could not extract text from PDF"
                    else:
                        # Limit text to avoid rate limits
                        text = text[:3000]

                        # SUMMARY
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

                        # QUESTIONS
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
