from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    username = data["username"]
    password = data["password"]

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Username already taken"}), 409

    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "user_id": user.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data or "username" not in data or "password" not in data:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    return jsonify({"success": True, "message": "Login successful", "user_id": user.id}), 200


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    user_id = data.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    old_password = data["old_password"]
    new_password = data["new_password"]

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({"success": False, "message": "Current password is incorrect"}), 401

    if old_password == new_password:
        return jsonify({"success": False, "message": "New password must be different from current password"}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"success": True, "message": "Password changed successfully"}), 200
