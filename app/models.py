from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db, login_manager
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import config

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __Tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), nullable=False)

    def get_reset_token(self, expires_second=1800):
        s = Serializer(config['default'].SECRET_KEY, expires_second)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod #tell python that the method is not the instance method
    def verify_reset_token(token):
        s = Serializer(config['default'].SECRET_KEY)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"""
                User: {self.name}
                Account Type: {self.type}"""

class Applicant(db.Model):
    __Tablename__ = "Applicants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(30), nullable=False)
    program = db.Column(db.String(255), nullable=False)
    document = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean)

    def __repr__(self):
        return f"""
                Student name: {self.name}
                Birthday: {self.birthday}
                Phone: {self.phone}
                Address: {self.address}
                                     """

class Student(db.Model):
    __Tablename__ = "Students"
    studentid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(30), nullable=False)
    program = db.Column(db.String(255), nullable=False)
    document = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"""
                Student ID: {self.studentid}
                Student name: {self.name}
                Birthday: {self.birthday}
                Phone: {self.phone}
                Address: {self.address}
                                     """

class Admin(db.Model):
    __Tablename__ = "Admins"
    adminID = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"""School: {self.school}
                   Username: {self.username}
                   Email: {self.email}"""

class Post(db.Model):
    __Tablename__ = "Posts"
    postid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    post = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
