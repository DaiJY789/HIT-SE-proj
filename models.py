from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    phoneNumber = db.Column(db.String(20), unique=False, nullable=True)
    location = db.Column(db.String(80), unique=False, nullable=True)
    photo = db.Column(db.String(120), nullable=True)  # 假设存储照片的路径或URL



class TutorInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    rate = db.Column(db.String(80), nullable=False)
    phoneNumber = db.Column(db.String(20), unique=False, nullable=False)
    information = db.Column(db.Text, unique=False, nullable=False)


class StudentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    budget = db.Column(db.String(80), nullable=False)
    phoneNumber = db.Column(db.String(20), unique=False, nullable=False)
    information = db.Column(db.Text, unique=False, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor_info.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    review = db.Column(db.Text, nullable=False)
