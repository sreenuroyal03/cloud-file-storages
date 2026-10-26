
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud File Storage</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef3f9;
            margin: 0;
            padding: 40px 15px;
        }
        .container {
            max-width: 700px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px #ccd3df;
        }
        h1 { color: #185adb; text-align: center; }
        p { text-align: center; color: #555; }
        .upload {
            background: #f4f7ff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        button, .download {
            background: #185adb;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
        }
        .file {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            padding: 12px 0;
            border-bottom: 1px solid #ddd;
            overflow-wrap: anywhere;
        }
        .message { color: #167a39; }
        .error { color: #c62828; }
    </style>
</head>
<body>
<div class="container">
    <h1>☁ Cloud File Storage</h1>
    <p>Upload and manage your files easily</p>

    {% if message %}
        <p class="{{ 'error' if error else 'message' }}">{{ message }}</p>
    {% endif %}

    <form class="upload" method="POST"
          enctype="multipart/form-data">
        <input type="file" name="file" required>
        <br><br>
        <button type="submit">Upload File</button>
    </form>

    <h2>My Stored Files</h2>

    {% if files %}
        {% for file in files %}
        <div class="file">
            <span>{{ file }}</span>
            <a class="download"
               href="{{ url_for('download_file', filename=file) }}">
               Download
            </a>
        </div>
        {% endfor %}
    {% else %}
        <p>No files uploaded yet.</p>
    {% endif %}
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    error = False

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename:
            filename = secure_filename(uploaded_file.filename)

            if not filename:
                message = "Invalid filename."
                error = True
            else:
                uploaded_file.save(UPLOAD_FOLDER / filename)
                message = "File uploaded successfully!"
        else:
            message = "Please select a file."
            error = True

    files = sorted(
        item.name for item in UPLOAD_FOLDER.iterdir()
        if item.is_file()
    )

    return render_template_string(
        HTML, files=files, message=message, error=error
    )


@app.route("/download/<filename>")
def download_file(filename):
    safe_name = secure_filename(filename)

    if not safe_name or safe_name != filename:
        return "Invalid filename", 400

    return send_from_directory(
        UPLOAD_FOLDER, safe_name, as_attachment=True
    )


@app.errorhandler(413)
def file_too_large(error):
    return "File is too large. Maximum size is 20 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)
