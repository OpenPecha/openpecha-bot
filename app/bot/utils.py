import requests
from github3.apps import create_jwt_headers

from . import app


def get_opf_layers_and_formats(pecha_id):
    meta_url = f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/meta.yml"
    content = requests.get(meta_url).content.decode()
    layer_names = []
    formats = [".epub", ".docx", ".md", ".txt"]
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
        app.config["GITHUBAPP_KEY"], app.config["GITHUBAPP_ID"]
    )

    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Status code : {response.status_code}, {response.json()}")
    return response.json()["id"]


def get_installation_access_token(installation_id):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = create_jwt_headers(
        app.config["GITHUBAPP_KEY"], app.config["GITHUBAPP_ID"]
    )

    response = requests.post(url=url, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Status code : {response.status_code}, {response.json()}")
    return response.json()["token"]


if __name__ == "__main__":
    layers = get_opf_layers("P000780")
    print(layers)
