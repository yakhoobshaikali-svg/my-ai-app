import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure your Google AI Key here
# Note: On Render, it's safer to use Environment Variables
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return "AI Server is Running!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    response = model.generate_content(user_message)
    return jsonify({"response": response.text})

# THIS PART IS FOR RENDER
if __name__ == "__main__":
    # Render provides a PORT variable, we must use it
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)