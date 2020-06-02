from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_github import GitHub

from bot import app, db_session
from bot.forms import InvitationForm, PechaIdForm, PechaSecretKeyForm
from bot.models import User

github = GitHub(app)


@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route("/")
def index():
    if session.get("user_id", None) is None:
        return render_template("login.html")
    else:
        return render_template("home.html")


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route("/github-callback")
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get("next") or url_for("home")
    if access_token is None:
        return redirect(next_url)

    user = User(access_token)
    g.user = user
    github_user = github.get("/user")
    github_user_id = github_user["id"]
    user = User.query.filter_by(github_id=github_user_id).first()
    if user is None:
        db_session.add(user)
        user.github_id = github_user_id
        user.github_login = github_user["login"]

    user.github_access_token = access_token
    g.user = user

    db_session.commit()

    session["user_id"] = user.id
    return redirect(next_url)


@app.route("/login")
def login():
    return github.authorize()


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/user")
def user():
    return jsonify(github.get("/user"))


@app.route("/repo")
def repo():
    return jsonify(github.get("/repos/cenkalti/github-flask"))


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/add-contributor")
def add_contributors():
    form = PechaSecretKeyForm()
    return render_template("secret_key_form.html", title="Pecha Secret Key", form=form)


@app.route("/join")
def join():
    form = PechaIdForm()
    return render_template("pecha_id_form.html", title="Join", form=form)
