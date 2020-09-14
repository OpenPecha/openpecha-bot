import { Octokit } from "https://cdn.skypack.dev/@octokit/core";

var editor = {
    init: function () {
        this.backend = new CodeMirror.fromTextArea($(".editor-textarea")[0], {
            mode: "hfml",
            lineNumbers: true,
            theme: "darcula"
        });
        this.backend.setSize(null, 800);
    },
    getValue: function () {
        return this.backend.getValue();
    }
}

async function fetchFileContent(volumeFileDom) {
    const download_url = $(volumeFileDom).children("#download-url").val();
    const response = await fetch(download_url);
    const content = await response.text();
    return content;
};

async function prepareTextEditorForm(volumeFileDom) {
    const text = await fetchFileContent(volumeFileDom);
    const org = $(volumeFileDom).children("#org").val();
    const repo = $(volumeFileDom).children("#repo").val();
    const branch = $(volumeFileDom).children("#branch").val();
    const path = $(volumeFileDom).children("#path").val();
    const sha = $(volumeFileDom).children("#sha").val();
    const editor_html = '\
        <form id="editor-form"> \
           <textarea class="editor-textarea">' + text + '</textarea> \
            <input type="hidden" id="org" value=' + org + '> \
            <input type="hidden" id="repo" value=' + repo + '> \
            <input type="hidden" id="branch" value=' + branch + '> \
            <input type="hidden" id="path" value=' + path + '> \
            <input type="hidden" id="sha" value=' + sha + '> \
            <br> \
            <button id="update-content" class="btn btn-primary">Save</button> \
        </form>';
    $('div.editor').html(editor_html);

    editor.init();
};

function addEditorTitle(volumeFileDom) {
    const volumeFilename = $(volumeFileDom).children("#volume-filename").text();
    $("p.editor-title").text(volumeFilename);
};

function launchEditor(volumeFileDom) {
    addEditorTitle(volumeFileDom);
    prepareTextEditorForm(volumeFileDom);
};

$(document).ready(function () {
    $("body").delegate("#volume-file", "click", function () {
        launchEditor(this);
    });
});

async function getOAuthToken() {
    const response = await fetch('/api/auth');
    const data = await response.json();
    return data['token'];
}

function utf8_to_b64(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}

async function pushChanges(org, repo, branch, path, message, content, sha) {
    const oauth_token = await getOAuthToken();
    const octokit = new Octokit({ auth: oauth_token });
    octokit.request('PUT /repos/{owner}/{repo}/contents/{path}', {
        owner: org,
        repo: repo,
        path: path,
        message: message,
        content: utf8_to_b64(content),
        sha: sha,
        branch: branch
    })
};

async function updateContent(editorForm) {
    const org = $(editorForm).children("#org").val();
    const repo = $(editorForm).children("#repo").val();
    const branch = $(editorForm).children("#branch").val();
    const path = $(editorForm).children("#path").val();
    const sha = $(editorForm).children("#sha").val();
    const content = editor.getValue();

    await pushChanges(org, repo, branch, path, "test message", content, sha);
};

$(document).ready(function () {
    $("body").delegate("#update-content", "click", function () {
        updateContent(this.parentElement);
    });
});