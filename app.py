import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
from groq import Groq

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not set in environment"}), 500

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
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text

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
        "Content:\n" + text_content[:4000]
    )

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        ai_output = response.choices[0].message.content
    except Exception as e:
        ai_output = f"Error generating summary: {str(e)}"

    return jsonify({"result": ai_output})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
