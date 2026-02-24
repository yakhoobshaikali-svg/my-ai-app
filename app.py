import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
from groq import Groq

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Create uploads folder if not exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")


# Home Route
@app.route("/")
def home():
    return render_template("index.html")


# Upload Route
@app.route("/upload", methods=["POST"])
def upload_file():

    # Get API Key from Render Environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not set in environment"}), 500

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    text_content = ""

    try:
        # Extract text from PDF
        if filename.lower().endswith(".pdf"):
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text

        # Extract text from TXT
        elif filename.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text_content = f.read()

        else:
            return jsonify({"error": "Only PDF and TXT files supported"}), 400

    except Exception as e:
        return jsonify({"error": f"File reading error: {str(e)}"}), 500

    if not text_content.strip():
        return jsonify({"error": "No text extracted from file"}), 400

    # Limit text size to avoid token overflow
    text_content = text_content[:4000]

    prompt = f"""
From the following study material:

1. Give a clear summary.
2. Provide important key points.
3. Generate 5 important exam questions.

Content:
{text_content}
"""

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )

        ai_output = response.choices[0].message.content

    except Exception as e:
        return jsonify({"error": f"Groq API error: {str(e)}"}), 500

    return jsonify({"result": ai_output})


# IMPORTANT for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
