from sqlalchemy.orm import backref
from ..db import db

import string
import random


from werkzeug.security import generate_password_hash, check_password_hash

from marshmallow import Schema, fields, validate

class UserModel(db.Model):

    __tablename__ = 'user'

    uid = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(128), nullable=False, unique=True)

    password_hash = db.Column(db.String(192), nullable=False)

    db_user_post = db.relationship('PostModel', backref='user')

    db_user_like = db.relationship('LikeModel', backref='user')

    db_user_comment = db.relationship('CommentModel', backref='user')

    def __init__(self, user_data):
        self.username = user_data['username']
        self.password = user_data['password']

    def __repr__(self) -> str:
        return f'Username: {self.username}, Password: {self.password}' 

    @property
    def password(self):
        raise AttributeError('passowrd is not readabilty attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_user(cls, username):
        return cls.query.filter_by(username = username).first()

    @classmethod
    def get_username_by_id(cls, uid):
        return cls.query.filter_by(uid = uid).first().username

    def save_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_random_password():
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
        length = 10
        password = []
        for i in range(length):
            password.append(random.choice(characters))

        ## shuffling the resultant password
        random.shuffle(password)
        random_password = "".join(password)
        return random_password


    
class UserSchema(Schema):
    uid = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(3))
    password = fields.String(required=True, validate=validate.Length(6))
