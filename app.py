from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def generate_summary(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
    return " ".join(sentences[:6]) if sentences else "Not enough content to summarize."


def generate_questions(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    questions = []

    keywords = ["is", "are", "was", "were", "can", "define", "explain", "describe"]

    for i, sentence in enumerate(sentences[:8]):
        words = sentence.split()
        if len(words) > 6:
            main_word = words[0]
            questions.append(f"Q{i+1}: What is meant by {main_word}?")
            questions.append(f"Q{i+1+1}: Explain the concept of {main_word}.")
        if len(questions) >= 5:
            break

    return questions if questions else ["No important questions generated."]


@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ""
    important_questions = []

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
                content = "Unsupported file type."

            content = content.replace('\n', ' ')
            summary = generate_summary(content)
            important_questions = generate_questions(content)

    return render_template('index.html', summary=summary, questions=important_questions)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
