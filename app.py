from flask import Flask, render_template, request
from google import genai
import os

app = Flask(__name__)

# Gemini API from Render Environment
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    summary = None
    questions = None

    if request.method == "POST":
        try:
            uploaded_file = request.files["file"]

            if uploaded_file:
                text = uploaded_file.read().decode("utf-8")

                response_summary = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"Summarize clearly for exam preparation:\n{text}"
                )

                response_questions = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"Generate 5 important exam questions:\n{text}"
                )

                summary = response_summary.text
                questions = response_questions.text.split("\n")

        except Exception as e:
            summary = f"AI Error: {str(e)}"

    return render_template("index.html",
                           summary=summary,
                           questions=questions)

if __name__ == "__main__":
    app.run()
