from flask import Flask, render_template, flash, request, url_for, redirect, session
from passlib.hash import sha256_crypt
import gc
from content_m import contact_info_content
from connection import connection_engine
from forms import RegistrationForm, CreatePostForm
from functools import wraps
import datetime
import os
import glob
from werkzeug.utils import secure_filename
from sqlalchemy import text

CONTACT_INFO = contact_info_content()

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
    return render_template("dashboard.html", DICT=CONTACT_INFO)


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


# logout


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out")
    gc.collect()
    return redirect(url_for('dashboard'))


# login


@app.route('/login/', methods=["GET", "POST"])
def login_page():
    error = ''
    try:
        if request.method == "POST":
            engine = connection_engine()
            with engine.connect() as c:
                data = c.execute(
                    text("SELECT * FROM users WHERE username = :username"), {"username": request.form['username']})

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
        error = "Invalid credentials, try again."
        flash(error)
        return render_template("login.html", error=error)


@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            engine = connection_engine()
            with engine.connect() as c:
                username = form.username.data
                email = form.email.data
                password = sha256_crypt.encrypt((str(form.password.data)))
                res = c.execute(
                    text("SELECT * FROM users WHERE username = :username"), {"username": username})
                if len(res.keys()) > 0:
                    flash("That username is already taken, please use another one")
                    return render_template('register.html', form=form)

                else:
                    c.execute(text("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)"),
                              {'username': username, 'password': password, 'email': email})

                    c.commit()
                    flash("Thanks for signin up!")

                    session['logged_in'] = True
                    session['username'] = username

                    gc.collect()
                    return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        msg = "Sometimes shit just popping"
        print(e)
        return str(msg)


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
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('add_post'))
    return render_template('add-post.html')


@app.route('/add-post/', methods=['POST', 'GET'])
@login_required
def add_post():
    try:
        form = CreatePostForm(request.form)

        if request.method == "POST" and form.validate():

            if form.post_title.data and form.post_text.data and form.post_filename.data:

                dt = datetime.date.today()
                post_date = dt.strftime("%d/%m/%y")
                engine = connection_engine()
                with engine.connect() as c:
                    query = "INSERT INTO posts (post_title, post_text, post_date, post_filename, post_username) " \
                            "values(:post_title, :post_text, :post_date, :post_filename, :username) "
                    c.execute(text(query),
                              {
                                  'post_title': form.post_title.data,
                                  'post_text': form.post_text.data,
                                  'post_date': post_date,
                                  'post_filename': form.post_filename.data,
                                  'username': session.get('username')
                              })

                    c.commit()

                    session['logged_in'] = True
                    flash('New post is created.')
                    posts = c.execute(text("SELECT post_title, post_text, post_username, post_date, post_filename "
                                           "FROM posts ORDER BY post_id DESC"))
                    gc.collect()
                    return redirect(url_for('news'), post_dict=posts)
            else:
                flash('Title and text should not be empty.')
                return render_template('add-post.html', username=session['username'], form=form)
        return render_template("add-post.html", form=form)

    except Exception as e:
        flash('You were not logged in. Please sign in first.')
        return str(e)


@app.route('/news/', methods=["GET", "POST"])
@login_required
def news():
    try:
        if session.get('username'):
            engine = connection_engine()
            with engine.connect() as c:
                posts = c.execute(text(
                    "SELECT post_title, post_text, post_username, post_date, post_filename FROM posts ORDER BY "
                    "post_id DESC"))
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
    songs = [os.path.basename(music)
             for music in glob.glob('static/uploads/*.mp3')]
    return render_template("music.html", songs=songs)


if __name__ == "__main__":
    app.run(debug=True)
