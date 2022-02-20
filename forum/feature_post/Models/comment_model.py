from marshmallow import Schema, fields, pre_load, validate
from ...db import db
from ...feature_auth.model import UserModel

from datetime import datetime

class CommentModel(db.Model):
    __tablename__ = 'comment'

    cid = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.Text, nullable=False)

    pub_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.pid'), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)

    def __init__(self, comment_data) -> None:
        self.post_id = comment_data['post_id']
        self.body = comment_data['body']
        self.author_id = comment_data['author_id']

    def __repr__(self) -> str:
        return f'User {self.author_id} commented post {self.post_id}'

    @classmethod
    def get_all_comment_post_id(cls, pid):
        return cls.query.filter_by(post_id=pid).all()

    @staticmethod
    def get_comment_author(author_id):
        author = UserModel.get_username_by_id(author_id)
        return author

    def save_db(self):
        db.session.add(self)
        db.session.commit()

class CommentSchema(Schema):
    cid = fields.Integer(dump_only=True)
    body = fields.String(required=True)