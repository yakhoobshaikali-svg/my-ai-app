from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
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

            # Extract content
            if filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "Unsupported file type. Please upload PDF or TXT."

            # Clean content
            content = content.replace('\n', ' ')
            sentences = content.split('.')

            # Generate Summary (First 5 meaningful sentences)
            meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
            summary = '. '.join(meaningful_sentences[:5]) + '.' if meaningful_sentences else "Not enough content to summarize."

            # Generate Important Questions
            for i, sentence in enumerate(meaningful_sentences[:5]):
                words = sentence.split()
                if len(words) > 5:
                    important_questions.append(
                        f"Q{i+1}: Explain {words[0]} {words[1]} {words[2]}."
                    )

    return render_template('index.html', summary=summary, questions=important_questions)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
