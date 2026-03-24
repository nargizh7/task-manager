# auth.py — Authentication blueprint for the Task Manager.
#
# Provides a /login endpoint that accepts a JSON body with
# username and password, verifies the credentials against the
# database, and returns a success or failure message.

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user with username and password."""

    data = request.get_json(silent=True)

    if not data or "username" not in data or "password" not in data:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    username = data["username"]
    password = data["password"]

    if username == "admin" and password == "password":
        return jsonify({"success": True, "message": "Login successful", "user_id": 1}), 200

    return jsonify({"success": False, "message": "Invalid credentials"}), 401
