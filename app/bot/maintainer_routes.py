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
from github3.apps import create_jwt_headers

from . import app, db_session
from .forms import PechaSecretKeyForm
from .models import Pecha, RoleType, User

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
    next_url = session.get("next")
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
    pecha_id = request.args.get("pecha_id")
    branch = request.args.get("branch")
    form = PechaSecretKeyForm()
    if form.validate_on_submit():
        secret_key = form.secret_key.data
        if len(secret_key) == 32:
            pecha = Pecha.query.filter_by(secret_key=secret_key).first()
            if pecha:
                flash("Correct Secret key!", "success")
                return redirect(
                    url_for(
                        "register_user",
                        pecha_id=pecha.id,
                        branch=branch,
                        is_owner=True,
                    )
                )
        flash("Invalid Pecha Secret Key!", "danger")
    context = {
        "title": "Enter Pecha Secret Key",
        "form": form,
        "pecha_id": pecha_id,
        "branch": branch,
        "is_owner": False,
    }
    return render_template("secret_key_form.html", **context)


@app.route("/register-user")
def register_user():
    pecha_id = request.args.get("pecha_id")
    branch = request.args.get("branch")
    is_owner = request.args.get("is_owner")

    if session.get("user_id", None) is None:
        session["next"] = url_for(
            "register_user", pecha_id=pecha_id, branch=branch, is_owner=is_owner
        )
        return github.authorize()

    user = User.query.get(session["user_id"])
    if is_owner:
        user.role = RoleType.owner
    else:
        user.role = RoleType.contributor
    user.pecha_id = pecha_id
    db_session.commit()
    send_invitation(user, pecha_id)

    return redirect(url_for("index", pecha_id=pecha_id, branch=branch))


def send_invitation(user, pecha_id):
    add_collaborator_url = f"https://api.github.com/repos/OpenPecha/{pecha_id}/collaborators/{user.github_login}"
    headers = {"Authorization": f"token {app.config['GITHUB_TOKEN']}"}
    res = github.session.request("PUT", add_collaborator_url, headers=headers)
    if res.status_code == 201:
        flash("Registration successful", "success")
    else:
        flash("Registration unsuccessful", "danger")


@app.route("/admin")
def admin_dashboard():
    pechas = Pecha.query.all()
    users = User.query.all()
    return render_template(
        "admin_page.html", title="Admin Page", pechas=pechas, users=users
    )
