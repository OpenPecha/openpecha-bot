import base64
import re
from pathlib import Path

import requests
from flask import current_app
from github3 import GitHub
from github3.apps import create_jwt_headers
from openpecha.formatters import HFMLFormatter
from openpecha.serializers import EpubSerializer, HFMLSerializer
from requests.api import head


def get_opf_layers_and_formats(pecha_id):
    meta_url = f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/meta.yml"
    content = requests.get(meta_url).content.decode()
    layer_names = []
    formats = [".epub"]
    for layer_name in content.split("layers:")[-1].split("-"):
        cleaned_layer_name = layer_name.strip()
        if not cleaned_layer_name:
            continue
        layer_names.append(cleaned_layer_name)
    return layer_names, formats


def get_installation_id(owner, repo):
    "https://developer.github.com/v3/apps/#find-repository-installation"
    url = f"https://api.github.com/repos/{owner}/{repo}/installation"
    headers = create_jwt_headers(
        current_app.config["GITHUBAPP_KEY"], current_app.config["GITHUBAPP_ID"]
    )

    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Status code : {response.status_code}, {response.json()}")
    return response.json()["id"]


def get_installation_access_token(installation_id):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = create_jwt_headers(
        current_app.config["GITHUBAPP_KEY"], current_app.config["GITHUBAPP_ID"]
    )

    response = requests.post(url=url, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Status code : {response.status_code}, {response.json()}")
    return response.json()["token"]


def create_issue(pecha_id, title, body=None, labels=[]):
    # Authenticating bot as an installation
    installation_id = get_installation_id(
        owner=current_app.config["GITHUBREPO_OWNER"], repo=pecha_id
    )
    installation_access_token = get_installation_access_token(installation_id)
    client = GitHub(token=installation_access_token)

    issue = client.create_issue(
        current_app.config["GITHUBREPO_OWNER"],
        pecha_id,
        title,
        body=body,
        labels=labels,
    )

    return issue


def create_export_issue(pecha_id, layers="", format_=".epub"):
    issue_title = "Export"
    issue_body = f"{','.join(layers)}\n{format_}"
    issue = create_issue(pecha_id, issue_title, body=issue_body, labels=["export"])
    return issue


def get_response_json(url, headers={}):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Status code : {response.status_code}, {response.json()}")
    return response.json()


class PechaExporter:
    """This class exports pecha into specified format with selected layers."""

    def __init__(self, pecha_id, layers="publication", format_=".epub"):
        self.pecha_id = pecha_id
        self.layers = layers
        self.format_ = format_

        self._prepare_paths()

        self.parser = HFMLFormatter(output_path=self.base_path)
        self.serializer = None

        self.content_url_template = (
            "https://api.github.com/repos/OpenPecha/{}/contents?ref={}"
        )

    def _prepare_paths(self):
        self.base_path = Path("/tmp") / "openpecha"
        self.pecha_path = self.base_path / self.pecha_id
        self.pecha_path.mkdir(exist_ok=True, parents=True)

        self.layers_path = self.pecha_path / "layers"
        self.layers_path.mkdir(exist_ok=True, parents=True)
        self.merged_layers_path = self.pecha_path / "merged_layers"
        self.merged_layers_path.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def _get_serializer(format_, **kwargs):
        if format_ == ".epub":
            return EpubSerializer(**kwargs)
        else:
            return HFMLSerializer(**kwargs)

    def _get_layers_git_urls(self):
        for layer in self.layers:
            files = get_response_json(
                self.content_url_template.format(self.pecha_id, layer)
            )
            for file in files:
                yield layer, file["name"], file["git_url"]

    @staticmethod
    def _get_content(git_url):
        data = get_response_json(git_url)
        return base64.b64decode(data["content"]).decode("utf-8")

    def download_layers(self):
        """Download layers."""
        for layer, fn, git_url in self._get_layers_git_urls():
            layer_path = self.layers_path / layer
            layer_path.mkdir(exist_ok=True)
            out_fn = layer_path / fn
            content = self._get_content(git_url)
            out_fn.write_text(content)

    def merge_layers(self):
        """Combine all the layer into one."""
        self.layers_path
        self.merged_layers_fn
        return

    def parse(self):
        """Parser layers into opf."""
        self.parser.create_opf(self.merged_layers_path)

    def serialize(self, opf_path):
        """Serialize the opf into given format."""
        serializers = self._get_serializer(self.format_, opf_path=opf_path)
        exported_fn = serializers.serialize(output_path=self.base_path)
        return exported_fn

    def create_pre_release(self):
        """Create pre-release and return the asset link."""
        return

    def clean(self):
        """Remove downloaded layers, hfml file, opf and exported file."""
        self.base_path.unlink()

    def export(self):
        self.download_layers()
        self.merge_layers()
        opf_path = self.parse()
        exported_asset_path = self.serialize(opf_path)
        asset_download_url = self.create_pre_release(exported_asset_path)
        self.clean()
        return asset_download_url


def create_export(pecha_id, layers, format_):
    exporter = PechaExporter(pecha_id, layers, format_)
    asset_download_url = exporter.export()
    return asset_download_url
