from ...db import db

class LikeModel(db.Model):
    __tablename__ = 'like'

    lid = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(db.Integer, db.ForeignKey('post.pid'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)

    def __init__(self, like_data) -> None:
        self.post_id = like_data['post_id']
        self.user_id = like_data['user_id']

    def __repr__(self) -> str:
        return super().__repr__()

    @classmethod
    def get_like_by_ids(cls, pid, uid):
        return cls.query.filter_by(post_id=pid, user_id=uid).first()
    
    @classmethod
    def check_like(cls, pid, uid):
        if cls.get_like_by_ids(pid, uid) == None:
            return False
        else:
            return True
        
    def save_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_like(self):
        db.session.delete(self)
        db.session.commit()

    