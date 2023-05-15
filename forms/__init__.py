# WTForms
from wtforms import Form, BooleanField, PasswordField, validators, TextAreaField, FileField, StringField
from wtforms.validators import DataRequired
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
    accept_tos = BooleanField(
        'I accept the <a href="/about/tos" target="blank"> Terms of Service </a> and <a href="/about/privacy-policy" '
        'target="blank">Privacy Notice</a>', [validators.DataRequired()])


"""
    Post form
"""


class CreatePostForm(Form):
    post_title = StringField('Title', validators=[DataRequired()])
    post_text = TextAreaField('Text', validators=[DataRequired()])
    post_filename = FileField('File', validators=[DataRequired()])
