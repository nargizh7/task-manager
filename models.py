# models.py — SQLAlchemy database models for the Task Manager application that:
# 1. defines two tables:
# User: stores account credentials and an optional profile image path
# Task: stores to-do items, each linked to a User via a foreign key

# 2. the design: 
# the user model includes profile_image in this correct version
# -> the high-frequency branch removes it, creating a cross-file dependency with upload.py
# -> tracing the attributeerror back to this file forces extra agent tool calls 
# -> tests whether experienced developers inspect cross-file edits more carefully 

from flask_sqlalchemy import SQLAlchemy

# create a single shared SQLAlchemy instance
# app.py will call db.init_app(app) to bind it to the Flask app
db = SQLAlchemy()

class User(db.Model):
    """Represents a registered user of the Task Manager."""

    __tablename__ = "users"

    # primary key — auto-incrementing int
    id = db.Column(db.Integer, primary_key=True)

    # username must be unique and non-null; is used for login
    username = db.Column(db.String(80), unique=True, nullable=False)

    # stores a hashed password (plain-text storage is intentionally avoided)
    password_hash = db.Column(db.String(256), nullable=False)

    # file-system path to the user's uploaded profile image
    # nullable because a user may not have uploaded one yet
    profile_image = db.Column(db.String(256), nullable=True)

    # a user can own many tasks.
    # backref creates a virtual owner attribute on each Task instance
    tasks = db.relationship("Task", backref="owner", lazy=True)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


class Task(db.Model):
    # a single to-do item owned by a User

    __tablename__ = "tasks"

    # PK
    id = db.Column(db.Integer, primary_key=True)

    #  title for the task (required)
    title = db.Column(db.String(200), nullable=False)

    # longer optional description of the task
    description = db.Column(db.Text, nullable=True)

    # False if not yet completed
    completed = db.Column(db.Boolean, default=False)

    # Foreign key linking every task to its owning user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} done={self.completed}>"
