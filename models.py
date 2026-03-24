# models.py — SQLAlchemy database models for the Task Manager.
#
# Defines two tables:
#   User  – account credentials
#   Task  – to-do items, each linked to a User via foreign key

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A registered user of the Task Manager."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

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
