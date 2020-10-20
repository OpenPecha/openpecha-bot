from uuid import uuid4

from flask import Blueprint, flash, redirect, request, url_for
from openpecha.config import PECHA_PREFIX

from .models import Pecha

blueprint = Blueprint("pecha", __name__, url_prefix="/pecha", static_folder="../static")


@blueprint.route("/create", methods=["POST"])
def create_pecha():
    title = request.form.get("title")
    sub_title = request.form.get("sub-title")
    author = request.form.get("author")
    sku = request.form.get("sku")
    front_cover_image = request.files.get("front-cover-image")
    publication_data_image = request.files.get("publication-data-image")
    content_images = request.files.getlist("content-images")
    content_text = request.form.get("content-text")
    print(
        title,
        sub_title,
        author,
        sku,
        front_cover_image,
        publication_data_image,
        content_images,
        content_text,
    )
    return "Create new pecha"


@blueprint.route("/secret", methods=["POST"])
def create_secret():
    for i in range(100, 101):
        pecha_id = f"P{i:06}"
        pecha = Pecha.query.filter_by(id=pecha_id).first()
        if pecha:
            continue
        Pecha.create(id=pecha_id, secret_key=uuid4().hex)
        print(f"added {pecha_id}")
    return redirect(url_for("user.admin_dashboard"))

    # pecha_id = request.form.get("pecha-id")
    # if pecha_id and not pecha_id.startswith(PECHA_PREFIX):
    #     flash(f"{pecha_id} is in valid", "danger")
    # pecha = Pecha.create(id=pecha_id, secret_key=uuid4().hex)
    # if pecha:
    #     flash(f"Secret Key successfully created for {pecha.id}", "success")
