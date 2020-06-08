import os


class Config:
    DEBUG = True

    # Database config
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")

    # Github app cofigs
    GITHUBAPP_ID = int(os.environ["GITHUBAPP_ID"])
    GITHUBAPP_SECRET = os.environ["GITHUBAPP_SECRET"]
    with open(os.environ["GITHUBAPP_KEY_PATH"], "rb") as key_file:
        GITHUBAPP_KEY = key_file.read()

    # Github Auth configs
    GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
    GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]

    # Github Auth Token
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
