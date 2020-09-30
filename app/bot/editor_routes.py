import time

import requests
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_github import GitHub

from . import app, db_session, utils
from .forms import PechaSecretKeyForm
from .models import Pecha, RoleType, User

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
        # add admin user
        if not user.role and user.username in app.config["OP_ADMIN_USERS"]:
            user.role = RoleType.admin
        db_session.add(user)
        db_session.commit()

    session["user_id"] = user.id
    return redirect(next_url)


@app.route("/login")
def login():
    return github.authorize()


@app.route("/logout")
def logout():
    pecha_id = request.args.get("pecha_id")
    branch = request.args.get("branch")
    session.pop("user_id", None)
    return redirect(url_for("index", pecha_id=pecha_id, branch=branch))


@app.route("/<pecha_id>")
def index(pecha_id):
    if "user_id" in session:
        return redirect(url_for("editor", pecha_id=pecha_id))
    session["next_url"] = url_for("editor", pecha_id=pecha_id)
    return render_template("login.html")


@app.route("/editor/<pecha_id>")
def editor(pecha_id):
    # login or register to github account
    if "user_id" not in session:
        return redirect(url_for("index", pecha_id=pecha_id))

    # Register user to text repo if not
    user = User.query.get(session["user_id"])
    if not user.pecha_id:
        return render_template("register.html", pecha_id=pecha_id)

    is_owner = False
    if user.role == RoleType.owner:
        is_owner = True
    layers, formats = utils.get_opf_layers_and_formats(pecha_id)
    return render_template(
        "main.html",
        pecha_id=pecha_id,
        layers=layers,
        formats=formats,
        is_owner=is_owner,
    )


@app.route("/validate-secret", methods=["GET", "POST"])
def validate_secret_key():
    pecha_id = request.args.get("pecha_id")
    form = PechaSecretKeyForm()
    if request.method != "POST":
        context = {
            "title": "Secret Key",
            "form": form,
            "pecha_id": pecha_id,
            "is_owner": False,
        }
        return render_template("secret_key_form.html", **context)

    if form.validate_on_submit():
        secret_key = form.secret_key.data
        if len(secret_key) == 32:
            pecha = Pecha.query.filter_by(secret_key=secret_key).first()
            if pecha:
                return redirect(
                    url_for("register_user", pecha_id=pecha.id, is_owner=True)
                )
        flash("Invalid Pecha Secret Key!", "danger")
        return redirect(url_for("index", pecha_id=pecha_id))


@app.route("/register-user", methods=["GET", "POST"])
def register_user():
    pecha_id = request.args.get("pecha_id")
    is_owner = request.args.get("is_owner")

    # Update pecha-id and role of the user
    user = User.query.get(session["user_id"])
    if is_owner == "True":
        user.role = RoleType.owner
    else:
        user.role = RoleType.contributor
    user.pecha_id = pecha_id
    db_session.commit()
    send_invitation(user, pecha_id)

    return redirect(url_for("editor", pecha_id=pecha_id))


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


def create_export_issue(pecha_id, layers="", format_=".epub"):
    issue_title = "Export"
    issue_body = f"{','.join(layers)}\n{format_}"
    issue = utils.create_issue(
        pecha_id, issue_title, body=issue_body, labels=["export"]
    )
    return issue


@app.route("/apply-layers", methods=["POST"])
def apply_layers():
    # Get layers and format
    pecha_id = request.args.get("pecha_id")
    layers = request.form.getlist("layers")
    format_ = request.form.getlist("format")

    # Create github issue
    export_issue = create_export_issue(pecha_id, layers, format_[0])

    if export_issue:
        flash(
            f"{pecha_id} is being exported. Please go to Download section to download the file",
            "info",
        )
    else:
        flash(f"{pecha_id} cloud not be exported. Please try again later", "danger")

    return redirect(url_for("index", pecha_id=pecha_id))


@app.route("/publish")
def publish():
    pecha_id = request.args.get("pecha_id")

    # Login with Github
    if session.get("user_id", None) is None:
        session["next_url"] = url_for("update", pecha_id=pecha_id)
        return github.authorize()

    user = User.query.get(session["user_id"])
    if user.role == RoleType.owner:
        issue_title = "Update OPF"
        issue_body = "create publish"
        issue = utils.create_issue(
            pecha_id, issue_title, body=issue_body, labels=["publish"]
        )

        if issue:
            flash(
                f"{pecha_id} is being updated. This may take a few minutes", "success"
            )
        else:
            flash(
                f"{pecha_id} cloud not be updated at the moment. Please try again later",
                "danger",
            )
    else:
        flash("Only owner can update the pecha", "danger")

    return redirect(url_for("index", pecha_id=pecha_id))


@app.route("/download/<org>/<pecha_export_fn>")
def download(org, pecha_export_fn):
    download_api_url = url_for(
        "download_api", org=org, pecha_export_fn=pecha_export_fn, _external=True
    )
    print(download_api_url)
    r = requests.get(download_api_url)
    return redirect(r.json()["download_url"])


@app.route("/admin")
def admin_dashboard():
    if session.get("user_id", None) is None:
        session["next_url"] = url_for("admin_dashboard")
        return render_template("login.html")

    user = User.query.get(session["user_id"])
    if user.username not in app.config["OP_ADMIN_USERS"]:
        return "You don't have access to this page"

    pechas = Pecha.query.all()
    users = User.query.all()
    return render_template(
        "admin_page.html", title="Admin Page", pechas=pechas, users=users
    )


# ~~~~~~ API ~~~~~~~


@app.route("/api/download/<org>/<pecha_export_fn>")
def download_api(org, pecha_export_fn):
    pecha_id, format_ = pecha_export_fn.split(".")
    json_response = {
        "pecha_id": pecha_id,
        "export_format": format_,
        "download_url": f"https://github.com/{org}/{pecha_id}/releases/latest/download/{pecha_export_fn}",
    }
    is_export_issue_created = False
    while True:
        r = requests.get(json_response["download_url"])
        if r.status_code == 200:
            return jsonify(json_response)
        else:
            if not is_export_issue_created:
                create_export_issue(pecha_id, format_=f".{format_}")
                is_export_issue_created = True
            time.sleep(5)


@app.route("/api/auth")
def auth():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            result = {"status": 200, "token": session["user_access_token"]}
        else:
            result = {"status": 404, "message": "User not registered."}
    else:
        result = {
            "status": 404,
            "message": "User not logged in. Please login to openpecha editor",
        }
    return jsonify(result)
