from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader  # for reading PDFs

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
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

            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "Unsupported file type. Please upload a PDF or TXT file."

            # Generate placeholder summary and questions
            summary = content[:500] + "..." if len(content) > 500 else content
            important_questions = [
                "Q1: Placeholder question 1?",
                "Q2: Placeholder question 2?",
                "Q3: Placeholder question 3?"
            ]

    return render_template('index.html', summary=summary, questions=important_questions)

if __name__ == '__main__':
    app.run(debug=True)
