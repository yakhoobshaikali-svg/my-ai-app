<!DOCTYPE html>
<html>
<head>
    <title>Smart Study AI</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            margin: 0;
            padding: 40px;
            text-align: center;
            color: white;
        }

        .college-header {
            font-size: 28px;
            font-weight: bold;
        }

        .college-address {
            font-size: 18px;
            margin-bottom: 25px;
        }

        .title {
            font-size: 24px;
            margin-bottom: 30px;
        }

        .container {
            background: white;
            color: black;
            padding: 30px;
            border-radius: 12px;
            max-width: 900px;
            margin: auto;
            box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
        }

        input[type="file"] {
            padding: 10px;
        }

        button {
            padding: 10px 20px;
            background: #007BFF;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #0056b3;
        }

        .result {
            text-align: left;
            margin-top: 30px;
            background: #f4f4f4;
            padding: 20px;
            border-radius: 10px;
        }

        .result h2 {
            color: #1e3c72;
        }

        .text-format {
            white-space: pre-wrap;
            line-height: 1.6;
        }

        .error {
            color: red;
            font-weight: bold;
            margin-top: 15px;
        }

    </style>
</head>

<body>

    <!-- College Name -->
    <div class="college-header">
        Gouthami Institute of Technology & Management for Women
    </div>

    <div class="college-address">
        Proddatur, Andhra Pradesh
    </div>

    <!-- Project Title -->
    <div class="title">
        📘 Smart Study AI – PDF Summary & Question Generator
    </div>

    <div class="container">

        <form action="/upload" method="POST" enctype="multipart/form-data">
            <input type="file" name="pdf_file" accept=".pdf" required>
            <br><br>
            <button type="submit">Upload & Generate</button>
        </form>

        {% if error %}
            <div class="error">
                {{ error }}
            </div>
        {% endif %}

        {% if summary %}
            <div class="result">
                <h2>📘 Summary</h2>
                <div class="text-format">
                    {{ summary }}
                </div>

                <h2>📝 Important Questions</h2>
                <div class="text-format">
                    {{ questions }}
                </div>
            </div>
        {% endif %}

    </div>

</body>
</html>
