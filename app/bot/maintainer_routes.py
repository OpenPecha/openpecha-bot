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
from bot.models import User

github = GitHub(app)


@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])


# @app.after_request
# def after_request(response):
#     db_session.remove()
#     return response


@app.route("/")
def index():
    return render_template("login.html")


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

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        db_session.add(user)

    user.github_access_token = access_token

    # Not necessary to get these details here
    # but it helps humans to identify users easily.
    g.user = user
    github_user = github.get("/user")
    user.github_id = github_user["id"]
    user.github_login = github_user["login"]

    db_session.commit()

    session["user_id"] = user.id
    return redirect(next_url)


@app.route("/login")
def login():
    if session.get("user_id", None) is None:
        return github.authorize()
    else:
        return "Already logged in"


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
