import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
from google import genai

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

# Configure Gemini API (new SDK)
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-1.5-flash"

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

    prompt = (
        "From the following study material:\n"
        "1. Give a clear summary.\n"
        "2. Provide important key points.\n"
        "3. Generate 5 important exam questions.\n\n"
        "Content:\n"
        + text_content[:4000]
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        ai_output = response.text
        if not ai_output:
            ai_output = "No summary generated. Check if your PDF has selectable text."
    except Exception as e:
        ai_output = f"Error generating summary: {str(e)}"

    return jsonify({"result": ai_output})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
