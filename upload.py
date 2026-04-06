# upload.py — Profile-image upload blueprint for the Task Manager.
#
# Provides a /upload endpoint that accepts a multipart file upload,
# saves the image to a configured upload directory, and records the
# file path on the corresponding User row.

import os

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from models import db, User

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename: str) -> bool:
    """Return True if *filename* has an allowed image extension."""
    return "." in filename and filename.rsplit(".", 1)[0].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_image():
    """Accept a profile-image upload and persist it for the given user."""

    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id"}), 400

    user = User.query.get(int(user_id))
    if user is None:
        return jsonify({"success": False, "message": "User not found"}), 404

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "File type not allowed"}), 400

    safe_name = secure_filename(file)

    os.makedirs(UPLOAD_DIR_PATH, exist_ok=True)

    dest_path = os.path.join(UPLOAD_DIR_PATH, safe_name)
    file.save(dest_path)

    user.profile_image = dest_path
    db.session.commit()

    return jsonify({"success": True, "message": "Image uploaded", "path": dest_path}), 200
