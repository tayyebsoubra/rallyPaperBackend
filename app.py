

import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://tayyebsoubra.github.io"])  # allow your GitHub Pages site


# ---------------- GOOGLE DRIVE SETUP ----------------
# Load service account credentials
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_FILE = "credentials.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# Folder ID in Google Drive where files will be uploaded
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return "Google Drive Upload Backend Running ✅"

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join("/tmp", filename)
    file.save(filepath)

    # Upload to Google Drive
    file_metadata = {
        "name": filename,
        "parents": [GOOGLE_DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(filepath, mimetype=file.content_type)
    uploaded_file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    os.remove(filepath)  # cleanup tmp file

    return jsonify(
        {
            "message": "Upload successful!",
            "fileId": uploaded_file.get("id"),
            "fileLink": uploaded_file.get("webViewLink"),
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
