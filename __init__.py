from flask import Flask, render_template, flash, request, url_for, redirect, session
from wtforms import Form, BooleanField, TextField, PasswordField, validators, TextAreaField, FileField
from wtforms.validators import DataRequired
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from content_m import content
from dbconnect import connection
from functools import wraps
import datetime
import os
import glob
from werkzeug.utils import secure_filename

DICT = content()


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = (['mp3', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
separator = (['mp3'])

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello():
    return render_template("main.html")


@app.route("/dashboard/")
def dashboard():
    flash("Flash test1")
    flash("Flash test2")
    return render_template("dashboard.html", DICT=DICT)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap

#logout
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    gc.collect()
    return redirect(url_for('dashboard'))

#login
@app.route('/login/', methods=["GET", "POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE username = %s",
                             [thwart(request.form['username'])])

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        # flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)

#WTForms class
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField(
        'I accept the <a href="/about/tos" target="blank">Terms of Service</a> and <a href="/about/privacy-policy" '
        'target="blank">Privacy Notice</a>', [validators.DataRequired()])


# Registration form
@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = %s", (username,))
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email)))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return str(e)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('add_post'))
        return render_template('addpost.html')


class ArticleForm(Form):
    post_title = TextField('post_title', validators=[DataRequired()])
    post_text = TextAreaField('post_text', validators=[DataRequired()])
    post_filename = FileField('post_filename', validators=[DataRequired()])


@app.route('/addpost/', methods=['POST', 'GET'])
@login_required
def add_post():
    try:
        form = ArticleForm(request.form)
        dt = datetime.date.today()
        post_date = dt.strftime("%d/%m/%y")

        if request.method == "POST" and form.validate():

            if form.post_title.data and form.post_text.data and form.post_filename.data:
                c, conn = connection()
                post = c.execute("INSERT INTO posts (post_title, post_text, post_date, post_filename, post_username)"
                                 "values(%s, %s, %s, %s, %s)",
                                 (form.post_title.data, form.post_text.data, post_date, form.post_filename.data,
                                  session.get('username')))
                conn.commit()
                flash('New post is created.')
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True

                return redirect(url_for('news'))
            else:
                flash('Title and text should not be empty.')
                return render_template('addpost.html', username=session['username'], form=form)
        return render_template("addpost.html", form=form)

    except Exception as e:
        flash('You were not logged in. Please sign in first.')
        return str(e)


@app.route('/news/', methods=["GET", "POST"])
@login_required
def news():
    try:
        if session.get('username'):
            c, conn = connection()
            posts = c.execute("SELECT post_title, post_text, post_username, post_date, post_filename"
                              " FROM posts ORDER BY post_id DESC")
            posts = c.fetchall()
            posts_dict = []
            for post in posts:
                post_dict = {
                    'post_title': post[0],
                    'post_text': post[1],
                    'post_username': post[2],
                    'post_date': post[3],
                    'post_filename': post[4]
                             }
                posts_dict.append(post_dict)
            return render_template('news.html', posts_dict=posts_dict)

    except Exception as e:
        return str(e)


@app.route("/music/", methods=["GET"])
@login_required
def music():
    songs = [os.path.basename(music) for music in glob.glob('static/uploads/*.mp3')]
    return render_template("music.html", songs=songs)

if __name__ == "__main__":
    app.run(debug=True)
