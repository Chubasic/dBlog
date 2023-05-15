from sqlalchemy import Column, Integer, String

from app import db


class Post(db.Model):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    post_title = Column(String(16), nullable=False)
    post_text = Column(String(200), nullable=False)
    post_username = Column(String(16), nullable=False)
    post_date = Column(String(40), nullable=False)
    post_filename = Column(String(18), nullable=True)

    def __init__(self, post_dict):
        self.post_date = post_dict.get('post_date', None)
        self.post_filename = post_dict.get('post_filename', None)
        self.post_text = post_dict.get('post_text', None)
        self.post_username = post_dict.get('post_username', None)
        self.post_title = post_dict.get('post_title', None)
