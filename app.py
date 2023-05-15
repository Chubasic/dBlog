from flask import Flask
from connection import conn_init_

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = (['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app: Flask = Flask(__name__)
app.secret_key = 'yeah'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite+pysqlite:///:memory:"
db = conn_init_(app=app)
from models.users import User
from models.posts import Post

with app.app_context():
    db.create_all()

# if __name__ == "__main__":
if __name__ == "app":
    from views import *
    app.run(debug=True)
