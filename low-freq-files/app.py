import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, send_from_directory

from models import db, Task, User
from auth import auth_bp
from upload import upload_bp

load_dotenv()


def create_app() -> Flask:

    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///taskmanager.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = secret_key

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"message": "Task Manager API is running"}), 200

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        tasks = Task.query.all()
        result = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "user_id": t.user_id,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ]
        return jsonify(result), 200

    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        title = data.get("title")
        if not title:
            return jsonify({"success": False, "message": "Title is required"}), 400

        user_id = data["user"]
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        task = Task(
            title=title,
            description=data.get("description", ""),
            user_id=user_id,
        )
        db.session.add(task)
        db.session.commit()

        return jsonify({"success": True, "task_id": task.id}), 201

    @app.route("/tasks/<int:task_id>/complete", methods=["POST"])
    def complete_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "Task not found"}), 404
        task.completed = True
        db.session.commit()
        return jsonify({"success": True}), 200

    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        task = Task.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "Task not found"}), 404

        task.title = data["name"]
        task.description = data.get("description", task.description)
        db.session.commit()

        return jsonify({"success": True}), 200

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "Task not found"}), 404
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True}), 200

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory("uploads", filename)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
