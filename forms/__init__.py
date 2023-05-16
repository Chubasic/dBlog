# WTForms
import os

from werkzeug.utils import secure_filename
from wtforms import Form, BooleanField, PasswordField, validators, TextAreaField, FileField, StringField
from wtforms.validators import DataRequired

from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

"""
    Registration form
"""


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


"""
    Post form
"""


class PostForm(Form):
    post_title = StringField('Title', validators=[DataRequired()])
    post_text = TextAreaField('Text', validators=[DataRequired()])
    post_filename = FileField('File', validators=[])

    def validate_image(self, field):
        filename = field.data
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def upload(self, request):
        if request.files.get('post_filename'):
            file = request.files.get('post_filename')
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            self.post_filename.data = file.filename
        # if self.post_filename.data:
        #     self.post_filename.data = request.files.get('post_filename').filename
        #     image_data = request.files[self.post_filename.name].read()
        #     open(os.path.join(upload_path, self.post_filename.data), 'w').write(image_data)
