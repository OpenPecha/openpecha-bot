import os

from bot import app
from flask import Flask
from flask_githubapp import GitHubApp

github_app = GitHubApp(app)


@github_app.on("issues.opened")
def cruel_closer():
    owner = github_app.payload["repository"]["owner"]["login"]
    repo = github_app.payload["repository"]["name"]
    num = github_app.payload["issue"]["number"]
    issue = github_app.installation_client.issue(owner, repo, num)
    issue.create_comment("Operation is being performed")
    issue.close()
