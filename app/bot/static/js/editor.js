import { Octokit } from "https://cdn.pika.dev/@octokit/core";

function getOAuthToken() {
    return fetch('/api/auth')
        .then(response => response.json())
        .then(data => { return data['token'] });
}

function pushChanges(repo, branch, path, message, content, sha) {
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

function viewFile(text) {
    const editor_html = '\
        <form id="editor-form"> \
            <textarea class="editor-textarea">' + text + '</textarea> \
            <br> \
            <button class="btn btn-primary">Save</button> \
        </form>';
    $('div.editor').html(editor_html);

    var editor = new CodeMirror.fromTextArea($(".editor-textarea")[0], {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        // theme: "dracula"
    });
    editor.setSize(null, 800);
};

function fetchFileContent(volumeFileDom) {
    const download_url = $(volumeFileDom).children("#download-url").val();
    return fetch(download_url)
        .then(response => response.text())
        .then(viewFile)
};

function addEditorTitle(volumeFileDom) {
    const volumeFilename = $(volumeFileDom).children("#volume-filename").text();
    $("p.editor-title").text(volumeFilename);
};

function launchEditor(volumeFileDom) {
    addEditorTitle(volumeFileDom);
    fetchFileContent(volumeFileDom);
};

$(document).ready(function () {
    $("body").delegate("#volume-file", "click", function () {
        launchEditor(this);
    });
});