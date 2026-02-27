from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("models/gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        text = request.form["content"]

        if not text.strip():
            return "Please enter study content."

        summary_response = model.generate_content(
            f"Summarize clearly for exam preparation:\n{text}"
        )
        summary = summary_response.candidates[0].content.parts[0].text

        question_response = model.generate_content(
            f"Generate 5 important exam questions:\n{text}"
        )
        questions = question_response.candidates[0].content.parts[0].text

        return render_template("index.html",
                               summary=summary,
                               questions=questions)

    except Exception as e:
        return f"AI Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
