import os
from flask import Flask, request
from PyPDF2 import PdfReader
from groq import Groq

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/")
def home():
    return """
    <h2>📘 Smart Study AI</h2>
    <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="pdf_file" accept=".pdf" required>
        <button type="submit">Upload & Generate</button>
    </form>
    """

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
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        if not text.strip():
            return "Could not extract text from PDF"

        # Limit text size to avoid rate limits
        text = text[:3000]

        # SUMMARY
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

        # QUESTIONS
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

        return f"""
        <h2>📘 Summary</h2>
        <pre>{summary}</pre>

        <h2>📝 Important Questions</h2>
        <pre>{questions}</pre>

        <br><br>
        <a href="/">⬅ Back</a>
        """

    except Exception as e:
        return f"Error occurred: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
