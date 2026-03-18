# models.py — SQLAlchemy database models for the Task Manager application that:

# 1. defines two tables:
# User: stores account credentials and an optional profile image path
# Task: stores to-do items, each linked to a User via a foreign key

# 2. the design:
# profile_image column is intentionally removed from this version
# -> when upload.py tries to set user.profile_image, it raises an attributeerror
# -> the agent has to trace the error from upload.py to this file (cross-file navigation)
# -> this forces extra read and edit tool calls, key for h1 and h2 prompt volume
# -> also lets us observe if experienced devs (h3) inspect cross-file changes more carefully

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    # a registered user of the Task Manager

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # bug 4 of 4 — profile_image column is missing
    # the agent has to trace an attributeerror from upload.py to this file, add the column, and handle db migration
    # placing this in a separate file forces extra read and edit prompts
    # key for reaching the prompt volume lets us observe if experienced devs inspect cross-file changes more carefully than beginners

    tasks = db.relationship("Task", backref="owner", lazy=True)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


class Task(db.Model):
    # a single to-do item owned by a User

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} done={self.completed}>"
