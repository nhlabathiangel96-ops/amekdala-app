from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Note(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(150))
    learning_style = db.Column(db.String(50), default="Not Set")
    notes = db.relationship('Note')


class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)  # The percentage (0-100)
    subject = db.Column(db.String(150))
    test_type = db.Column(db.String(50))  # e.g., "Pre-Test" or "Post-Test"
    # Automatically saves the date
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

    # Link this result to the user who took it
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
