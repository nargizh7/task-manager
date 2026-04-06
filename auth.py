# auth.py — Authentication blueprint for the Task Manager that:
# 1. provides a /login endpoint that accepts a JSON body with username and password
# 2. verifies the credentials against the database, and returns a success or failure message

# the design:
# auth lives in its own file so that in the low-frequency branch we can
# swap just this file with a buggy version. the agent only needs to
# read and edit auth.py, keeping prompt count low (h1 baseline)

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():

    # expects JSON: {"username": "...", "password": "..."}
    # returns JSON with a success flag and message
    data = request.get_json(silent=True)

    if not data or "username" not in data or "password" not in data:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    username = data["username"]
    password = data["password"]

    # look up the user by username
    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    # verify the password against the stored hash
    if not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    return jsonify({"success": True, "message": "Login successful", "user_id": user.id}), 200
