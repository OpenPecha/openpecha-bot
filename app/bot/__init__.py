import os

from flask import Flask
from flask_githubapp import GitHubApp

app = Flask(__name__)

# Github app cofigs
app.config["GITHUBAPP_ID"] = int(os.environ["GITHUBAPP_ID"])
app.config["GITHUBAPP_SECRET"] = os.environ["GITHUBAPP_SECRET"]
with open(os.environ["GITHUBAPP_KEY_PATH"], "rb") as key_file:
    app.config["GITHUBAPP_KEY"] = key_file.read()


from bot import routes
