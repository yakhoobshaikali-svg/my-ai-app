from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import google.generativeai as genai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def generate_ai_content(text):
    prompt = f"""
You are an academic assistant.

From the following study material:

1. Generate a clear academic summary (200–300 words).
2. Generate 8 important university-level exam questions.
3. Questions must be meaningful and based strictly on the content.

Content:
{text[:4000]}
"""

    response = model.generate_content(prompt)
    return response.text


@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ""
    questions = []

    if request.method == 'POST':
        file = request.files.get('file')

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ""

            ai_output = generate_ai_content(content)

            parts = ai_output.split("Questions")
            summary = parts[0]
            questions = parts[1].split("\n") if len(parts) > 1 else []

    return render_template('index.html', summary=summary, questions=questions)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
