from flask import Flask, render_template, request
from groq import Groq
import PyPDF2
import os

app = Flask(__name__)

# Use environment variable (important for Render)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    if "pdf_file" not in request.files:
        return render_template("index.html", error="No file uploaded")

    file = request.files["pdf_file"]

    if file.filename == "":
        return render_template("index.html", error="Please select a PDF file")

    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        if not text.strip():
            return render_template("index.html", error="Could not extract text from PDF")

        text = text[:4000]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"""
From the following text:

{text}

Give:
1) Clear Summary
2) 10 Important Exam Questions (numbered)
"""
                }
            ],
            temperature=0.3,
        )

        result = response.choices[0].message.content

        return render_template("index.html", summary=result)

    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
