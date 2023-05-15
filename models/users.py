from sqlalchemy import Column, Integer, String
from app import db


class User(db.Model):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(16), nullable=False)
    email = Column(String(60), key="email", unique=True)
    password = Column(String(18), nullable=False)

    def __init__(self, user_dict):
        self.email = user_dict.get('email', None)
        self.password = user_dict.get('password', None)
        self.nickname = user_dict.get('nickname', None)

    def create_new_user(self):
        print("Creating user named", self.nickname)
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def exists(email):
        return User.query.filter_by(email=email).first()
