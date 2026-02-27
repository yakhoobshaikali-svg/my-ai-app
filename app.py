from flask import Flask, render_template, request
from google import genai
import os

app = Flask(__name__)

# Use environment variable in Render
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        text = request.form["content"]

        if not text.strip():
            return "Please enter study content."

        response_summary = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Summarize clearly for exam preparation:\n{text}"
        )

        response_questions = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Generate 5 important exam questions:\n{text}"
        )

        return render_template("index.html",
                               summary=response_summary.text,
                               questions=response_questions.text)

    except Exception as e:
        return f"AI Error: {str(e)}"

if __name__ == "__main__":
    app.run()
