from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error":"No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error":"No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # ==== AI Processing Simulation ====
    # Replace this part with your AI summary + questions logic
    summary = f"This is a simulated summary for {file.filename}."
    questions = [
        "What is the main topic?",
        "List 3 key points.",
        "Explain the conclusion."
    ]

    return jsonify({"summary": summary, "questions": questions})

if __name__ == '__main__':
    app.run(debug=True)
