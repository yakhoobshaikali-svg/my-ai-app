from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import google.generativeai as genai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if not exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Use stable working model
model = genai.GenerativeModel("gemini-1.0-pro")


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def generate_ai_content(text):
    try:
        prompt = f"""
You are an academic assistant.

From the following study material:

1. Write a well-structured academic summary (200–300 words).
2. Generate 8 meaningful university-level exam questions.
3. Questions must strictly depend on the content.
4. Clearly separate summary and questions.
5. Format questions as numbered list.

Content:
{text[:3500]}
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"AI_ERROR::{str(e)}"


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

            # Extract content
            if filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ""

            content = content.replace('\n', ' ')

            ai_output = generate_ai_content(content)

            # If AI failed
            if ai_output.startswith("AI_ERROR::"):
                summary = "Error generating AI content."
                questions = [ai_output]
            else:
                # Split summary and questions safely
                lines = ai_output.split("\n")
                summary_lines = []
                question_lines = []

                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith(tuple(str(i) for i in range(1, 10))):
                        question_lines.append(stripped)
                    else:
                        summary_lines.append(stripped)

                summary = " ".join(summary_lines)
                questions = question_lines

    return render_template('index.html', summary=summary, questions=questions)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
