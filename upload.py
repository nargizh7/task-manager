# upload.py — Profile-image upload blueprint for the Task Manager that:
# 1. provides a /upload endpoint that accepts a multipart file upload
# 2. saves the image to a configured upload directory
# 3. records the path on the corresponding User row

# the design: 
# the upload route is in its own file so that the high-frequency branch can place cascading bugs here and in models.py
# -> this forces the agent to navigate across files, producing more tool calls
# -> permission prompts 

import os

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from models import db, User

# blueprint for upload-related routes
upload_bp = Blueprint("upload", __name__)

# restrict accepted file extensions to common image types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")


def allowed_file(filename: str) -> bool:
    # True if filename has an allowed image extension
    # check the lowered extension against the set
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_image():

    # validate user_id 
    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id"}), 400

    user = User.query.get(int(user_id))
    if user is None:
        return jsonify({"success": False, "message": "User not found"}), 404

    # validate uploaded file 
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "File type not allowed"}), 400

    # sanitise the filename to prevent directory-traversal attacks
    safe_name = secure_filename(file.filename)

    # ensure the upload directory exists; create it if necessary
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # build the full destination path and write the file
    dest_path = os.path.join(UPLOAD_DIR, safe_name)
    file.save(dest_path)

    # store the relative path so the app can serve or reference it later
    user.profile_image = dest_path
    db.session.commit()

    return jsonify({"success": True, "message": "Image uploaded", "path": dest_path}), 200
