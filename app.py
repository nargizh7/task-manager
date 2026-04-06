# app.py — Application factory and entry point for the Task Manager that:
#  1. configures the Flask application instance
#  2. initialzies the SQLAlchemy database connection
#  3. registers the auth and upload blueprints
#  4. provides a simple index route and a route to list tasks

# server will start on http://127.0.0.1:5000 in debug mode.

# study design: the app is split across four files so that debugging requires the agent to navigate between modules. 
# this produces more tool calls and permission prompts, which is the core mechanism for the high-frequency condition.

import os

from flask import Flask, jsonify

from models import db, Task, User
from auth import auth_bp
from upload import upload_bp


def create_app() -> Flask:

    app = Flask(__name__)

    # use an in-memory SQLite database by default -> override by setting the DATABASE_URL env variable
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///taskmanager.db"
    )

    # disable the Flask-SQLAlchemy event system (not needed but saves memory)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # secret key used to sign session cookies
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # bind the shared SQLAlchemy instance (from models.py) to this app
    db.init_app(app)

    # each blueprint adds its routes under the default URL prefix 
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)

    # create_all is safe to call repeatedly — it only creates tables that do not already exist
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        """Health-check / landing endpoint."""
        return jsonify({"message": "Task Manager API is running"}), 200

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        """Return every task in the database as a JSON list."""
        tasks = Task.query.all()
        result = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "user_id": t.user_id,
            }
            for t in tasks
        ]
        return jsonify(result), 200

    return app

# when this file is executed directly -> build the app and start the dev server
if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
