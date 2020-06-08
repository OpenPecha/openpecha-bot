from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_github import GitHub

from . import app, db_session
from .forms import PechaSecretKeyForm
from .models import Pecha, User

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
        user = User(access_token)
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


@app.route("/<pecha_id>/<branch>")
def index(pecha_id, branch):
    return render_template("main.html", pecha_id=pecha_id, branch=branch)
    # if session.get("user_id", None) is None:
    #     return render_template("login.html")


@app.route("/validate-secret", methods=["GET", "POST"])
def validate_secret_key():
    form = PechaSecretKeyForm()
    if form.validate_on_submit():
        secret_key = form.secret_key.data
        if len(secret_key) == 32:
            pecha = Pecha.query.filter_by(secret_key=secret_key).first()
            print(pecha)
            if pecha:
                flash("Correct Secret key!", "success")
                return redirect(url_for("register_collaborator", pecha_id=pecha.id))
        flash("Invalid Pecha Secret Key!", "danger")
    return render_template("secret_key_form.html", title="Pecha Secret Key", form=form)


@app.route("/register-collaborator/<pecha_id>")
def register_collaborator(pecha_id):
    print(pecha_id)
    return pecha_id


@app.route("/admin")
def admin_dashboard():
    pechas = Pecha.query.all()
    return render_template("admin_page.html", title="Admin Page", pechas=pechas)
