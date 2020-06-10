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
from .utils import get_opf_layers_and_formats

github = GitHub(app)


@github.access_token_getter
def token_getter():
    return session.get("user_access_token", None)


@app.route("/github-callback")
@github.authorized_handler
def authorized(access_token):
    next_url = session.get("next_url")
    if access_token is None:
        flash("Authorization failed.", category="error")
        return redirect(next_url)
    session["user_access_token"] = access_token
    github_user = github.get("/user")
    user = User.query.filter_by(username=github_user["login"]).first()

    # add user to database
    if user is None:
        user = User(username=github_user["login"])
        db_session.add(user)
        db_session.commit()

    session["user_id"] = user.id
    return redirect(next_url)


def logout():
    session.pop("user_id", None)


@app.route("/<pecha_id>/<branch>")
def index(pecha_id, branch):
    layers, formats = get_opf_layers_and_formats(pecha_id)
    return render_template(
        "main.html", pecha_id=pecha_id, branch=branch, layers=layers, formats=formats
    )


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

    # Login with Github
    if session.get("user_id", None) is None:
        session["next_url"] = url_for(
            "register_user", pecha_id=pecha_id, branch=branch, is_owner=is_owner
        )
        return github.authorize()

    # Update pecha-id and role of the user
    user = User.query.get(session["user_id"])
    if is_owner:
        user.role = RoleType.owner
    else:
        user.role = RoleType.contributor
    user.pecha_id = pecha_id
    db_session.commit()
    send_invitation(user, pecha_id)

    # Logout after registration
    logout()

    return redirect(url_for("index", pecha_id=pecha_id, branch=branch))


def send_invitation(user, pecha_id):
    add_collaborator_url = f"https://api.github.com/repos/OpenPecha/{pecha_id}/collaborators/{user.username}"
    headers = {"Authorization": f"token {app.config['GITHUB_TOKEN']}"}
    res = github.session.request("PUT", add_collaborator_url, headers=headers)
    if res.status_code == 201:
        flash(
            f"Please check your Github linked Email to complete the Registration to {pecha_id}",
            "info",
        )
    elif res.status_code == 204:
        flash(f"User already registered to {pecha_id}", "info")
    else:
        flash("Registration failed. Please try again later", "danger")


@app.route("/apply-layers", methods=["POST"])
def apply_layers():
    layers = request.form.getlist("layers")
    formats = request.form.getlist("format")
    return ", ".join(layers + formats)


@app.route("/admin")
def admin_dashboard():
    # global NEXT_URL
    # if session.get("user_id", None) is None:
    #     NEXT_URL = url_for("admin_dashboard")
    #     return github.authorize()

    # user = User.query.get(session["user_id"])
    # if user.role != RoleType.admin:
    #     return "You don't have access to this page"

    pechas = Pecha.query.all()
    users = User.query.all()
    return render_template(
        "admin_page.html", title="Admin Page", pechas=pechas, users=users
    )
