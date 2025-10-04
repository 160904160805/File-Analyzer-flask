from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
from analyzer import analyze_file

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

# Folder to store uploads & reports
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    """Home page - File upload form"""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and trigger analysis"""
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(request.url)

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Analyze file and generate reports
        reports = analyze_file(filepath, app.config["UPLOAD_FOLDER"])

        flash("File uploaded and analyzed successfully!")
        return render_template("index.html", reports=reports)


@app.route("/download/<filename>")
def download_file(filename):
    """Allow users to download generated reports"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)