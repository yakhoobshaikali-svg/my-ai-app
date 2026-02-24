import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
import google.generativeai as genai

# Optional OCR libraries
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Create uploads folder if not exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Configure Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    text_content = ""

    # Extract text from PDF
    if filename.endswith(".pdf"):
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text

        # If PDF has no selectable text and OCR is available
        if not text_content.strip() and OCR_AVAILABLE:
            pages = convert_from_path(filepath)
            for page in pages:
                text_content += pytesseract.image_to_string(page)

    # Extract text from TXT
    elif filename.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text_content = f.read()
    else:
        return jsonify({"error": "Only PDF and TXT supported"}), 400

    if not text_content.strip():
        return jsonify({"error": "No text extracted from file"}), 400

    # Limit text for Gemini prompt (first 4000 chars)
    prompt = f"""
From the following study material:

1. Give a clear summary.
2. Provide important key points.
3. Generate 5 important exam questions.

Content:
{text_content[:4000]}
"""

    # Call Gemini API
    try:
        response = model.generate_content(prompt)
        ai_output = getattr(response, "output_text", None)
        if not ai_output:
            ai_output = "No summary generated. Check if your PDF has selectable text."
    except Exception as e:
        ai_output = f"Error generating summary: {str(e)}"

    return jsonify({"result": ai_output})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
