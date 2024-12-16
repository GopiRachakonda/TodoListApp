from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the database instance
db = SQLAlchemy()


# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Relationship to tasks
    tasks = db.relationship('Task', backref='owner', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


# Task Model
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Time task was created
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign Key to User table

    def __repr__(self):
        return f"<Task {self.content}, Completed: {self.completed}>"
