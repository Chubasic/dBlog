import datetime
import gc
import os
from functools import wraps

from flask import render_template, flash, request, url_for, redirect, session
from passlib.hash import sha256_crypt
from app import app, db
from content_m import contact_info_content
from forms import RegistrationForm, PostForm
from models.posts import Post
from models.users import User

CONTACT_INFO = contact_info_content()


@app.route('/')
def hello():
    return render_template("main.html")


@app.route("/dashboard/")
def dashboard():
    default: str = "No data"
    return render_template("dashboard.html", CONTACT_INFO=CONTACT_INFO, email=session.get('email', default),
                           username=session.get("nickname", default))


@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('An error occurred', e)
    return render_template("404.html")


@app.errorhandler(500)
def page_not_found(e):
    app.logger.error('An error occurred', e)
    return render_template("error.html", error=e)


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

            user = db.session.get(User, {'nickname': request.form['username']})
            if sha256_crypt.verify(request.form['password'], user.password):
                session['logged_in'] = True
                session['nickname'] = request.form['username']
                session['email'] = user.email
                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        return render_template("login.html", error=error)

    except Exception as e:
        error = "Invalid credentials, try again."
        flash(error)
        app.logger.error('An error occurred', e)
        return render_template("login.html", error=error)


@app.route('/register/', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            nickname: str = form.username.data
            email: str = form.email.data
            password: str = sha256_crypt.hash(form.password.data)
            res = User.exists(email=email)
            app.logger.info(f"User exists?::> ${res}", )
            if res:
                flash("You already have account, login with your password.")
                return render_template('register.html', form=form)

            else:

                try:
                    user = User(dict(nickname=nickname, password=password, email=email))
                    user.create_new_user()
                    session['logged_in'] = True
                    session['nickname'] = nickname
                    session['email'] = email
                    flash("Thanks for signin up!")
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    return render_template("error.html", error=e)
        return render_template("register.html", form=form)

    except Exception as e:
        flash("Ah yes, this one, something broke up, sorry bro.")
        return render_template("error.html", error=e)


@app.route('/add-post/', methods=['POST', 'GET'])
@login_required
def add_post():
    form = PostForm(request.form)
    try:
        form.upload(request)
        if request.method == "POST" and form.validate():
            if form.post_title.data and form.post_text.data:
                dt = datetime.date.today()
                post_date = dt.strftime("%d/%m/%y")
                post = Post({
                    'post_title': form.post_title.data,
                    'post_text': form.post_text.data,
                    'post_date': post_date,
                    'post_filename': form.post_filename.data,
                    'post_username': session.get('nickname', "Anonymous")
                })
                app.logger.info({
                    'post_title': form.post_title.data,
                    'post_text': form.post_text.data,
                    'post_date': post_date,
                    'post_filename': form.post_filename.data,
                    'post_username': session.get('nickname', "Anonymous")
                })
                db.session.add(post)
                db.session.commit()

                flash('New post is created.')
                return redirect(url_for('news'))
            else:
                flash('Bad request.')
                return render_template('add-post.html', username=session.get('nickname', "Unknown"), form=form)
    except Exception as e:
        flash('Nope, not working ;)')
        return render_template("error.html", error=e)
    return render_template("add-post.html", form=form)


@app.route('/news/', methods=["GET", "POST"])
@login_required
def news():
    try:
        posts_list = []
        posts = db.session.query(Post).all()
        for post in posts:
            post_dict = {
                'post_title': post.post_title,
                'post_text': post.post_text,
                'post_username': post.post_username,
                'post_date': post.post_date,
                'post_filename': post.post_filename
            }
            posts_list.append(post_dict)
        return render_template('news.html', posts_list=posts_list)

    except Exception as e:
        flash("Something went wrong")
        return render_template("error.html", error=e)
