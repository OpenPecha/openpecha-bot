import { Octokit } from "https://cdn.pika.dev/@octokit/core";

function getOAuthToken() {
    return fetch('/api/auth')
        .then(response => response.json())
        .then(data => { return data['token'] });
}

export function pushChanges(repo, branch, path, message, content, sha) {
    const oauth_token = getOAuthToken();
    const octokit = new Octokit({ auth: oauth_token });
    octokit.request('PUT /repos/{owner}/{repo}/contents/{path}', {
        owner: 'OpenPecha',
        repo: repo,
        path: path,
        message: message,
        content: window.btoa(content),
        sha: sha,
        branch: branch
    })
};
