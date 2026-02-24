import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Create uploads folder if not exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

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

    if filename.endswith(".pdf"):
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    text_content += page.extract_text()
    elif filename.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text_content = f.read()
    else:
        return jsonify({"error": "Only PDF and TXT supported"}), 400

    if not text_content.strip():
        return jsonify({"error": "No text extracted from file"}), 400

    prompt = f"""
    From the following study material:

    1. Give a clear summary.
    2. Provide important key points.
    3. Generate 5 important exam questions.

    Content:
    {text_content[:4000]}
    """

   response = model.generate_content(prompt)

# Safely extract text from Gemini response
ai_output = None
if hasattr(response, "text") and response.text:
    ai_output = response.text
elif hasattr(response, "candidates"):
    try:
        ai_output = response.candidates[0].content.parts[0].text
    except Exception:
        ai_output = "No summary generated."

if not ai_output:
    ai_output = "No summary generated. Check if your PDF has selectable text."

return jsonify({"result": ai_output})



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
