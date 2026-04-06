# upload.py — Profile-image upload blueprint for the Task Manager that:

# 1. provides a /upload endpoint that accepts a multipart file upload
# 2. saves the image to a configured upload directory
# 3. records the path on the corresponding User row

import os

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from models import db, User

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename: str) -> bool:
    # True if filename has an allowed image extension
    # bug 1 of 4 — index [0] checks the name stem instead of the extension
    # this is a logic error not a crash, so the agent has to reason about the string splitting rather than just read a traceback
    # starts the high-frequency prompt cascade 
    return "." in filename and filename.rsplit(".", 1)[0].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_image():

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

    # bug 2 of 4 — passes the file object instead of file.filename
    # -> werkzeug raises a typeerror
    # second crash after fixing bug 1
    # -> each fix-rerun cycle adds more permission prompts 
    safe_name = secure_filename(file)

    # bug 3 of 4 — upload_dir_path is never defined at module level
    # raises a nameerror after bug 2 is fixed. third debug cycle
    os.makedirs(UPLOAD_DIR_PATH, exist_ok=True)

    dest_path = os.path.join(UPLOAD_DIR_PATH, safe_name)
    file.save(dest_path)

    # bug 4 of 4 continues in models.py — profile_image column is missing from the user model
    # -> Forces the agent to search and read a second file, adding cross-file tool calls
    # this is where we expect prompt volume
    user.profile_image = dest_path
    db.session.commit()

    return jsonify({"success": True, "message": "Image uploaded", "path": dest_path}), 200
