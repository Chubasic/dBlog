from flask_sqlalchemy import SQLAlchemy


def conn_init_(app):
    db = SQLAlchemy()
    db.init_app(app)
    return db
