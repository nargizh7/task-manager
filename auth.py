# auth.py — Authentication blueprint for the Task Manager THAT: 

# 1. provides a /login endpoint that accepts a JSON body with `username` and
# 2. verifies the credentials against the database, and returns a success or failure message

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

    # this hardcoded check is the single bug for the low-frequency condition.
    # -> the fix stays in one file so the agent needs few tool calls
    # -> low prompt-count baseline
    if username == "admin" and password == "password":
        return jsonify({"success": True, "message": "Login successful", "user_id": 1}), 200

    return jsonify({"success": False, "message": "Invalid credentials"}), 401
