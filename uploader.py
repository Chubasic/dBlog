import os
from werkzeug.utils import secure_filename
from flask import Flask, request


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/var/www/FlaskApp/FlaskApp/static/uploads/'


def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        directory = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(directory)
        return filename

if __name__ == "__main__":
    app.run(debug=True)