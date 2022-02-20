from marshmallow import Schema, fields, pre_load, validate
from sqlalchemy.sql.sqltypes import String
from ...db import db
from ...feature_auth.model import UserModel

from datetime import datetime

ALLOWED_TAGS = ['General', 'Music', 'Sport', 'Anime']

class PostModel(db.Model):
    __tablename__ = 'post'

    pid = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(40), nullable=False)

    body = db.Column(db.Text, nullable=False)

    tag = db.Column(db.String(10), nullable=False)

    pub_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)

    db_post_like = db.relationship('LikeModel', backref='post')

    db_post_comment = db.relationship('CommentModel', backref='post')

    def __init__(self, post_data):
        self.title = post_data['title']
        self.body = post_data['body']
        self.author_id = post_data['author_id']
        if post_data['tag'] not in ALLOWED_TAGS:
            self.tag = ALLOWED_TAGS[0]
        else:
            
            self.tag = post_data['tag']

    def __repr__(self):
        return f'Post title:{self.title}, Post id: {self.pid} with tag {self.tag}'

    @classmethod
    def get_post_by_id(cls, id: int):
        return cls.query.filter_by(pid=id).first()
        
    @classmethod
    def get_posts_by_tag(cls, tag: String):
        return cls.query.filter_by(tag=tag).all()

    @classmethod
    def get_all_post(cls):
        return cls.query.all()

    @staticmethod
    def get_post_author(author_id):
        author = UserModel.get_username_by_id(author_id)
        return author

    def save_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_post(self):
        db.session.delete(self)
        db.session.commit()

class PostSchema(Schema):
    pid = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    body = fields.String(required=True)
    tag = fields.String(required=True)
