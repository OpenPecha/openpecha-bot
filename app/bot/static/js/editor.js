import { listFiles } from "./files.js";
import { getGHClient } from "./github.js";

var editor = {
    init: function () {
        this.backend = new CodeMirror.fromTextArea($(".editor-textarea")[0], {
            mode: "hfml",
            lineNumbers: true,
            theme: "darcula",
            extraKeys: {
                "F11": function (cm) {
                    cm.setOption("fullScreen", !cm.getOption("fullScreen"));
                },
                "Esc": function (cm) {
                    if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
                }
            }
        });
        this.backend.setSize(null, 800);
    },
    getValue: function () {
        return this.backend.getValue();
    }
}


function b64_to_utf8(str) {
    return decodeURIComponent(escape(window.atob(str)));
}

function utf8_to_b64(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}

async function getBlob(owner, repo, sha) {
    const ghClient = await getGHClient();
    const gh_response = await ghClient.request('GET /repos/{owner}/{repo}/git/blobs/{file_sha}', {
        owner: owner,
        repo: repo,
        file_sha: sha
    })

    const response = await fetch(gh_response['url'])
    const data = await response.json()
    return data['content']
}

async function prepareTextEditorForm(volumeFileDom) {
    const sha = $(volumeFileDom).children("#sha").val();
    const path = $(volumeFileDom).children("#path").val();

    const data = await getBlob(window.gh_org, window.gh_repo, sha)

    const editor_html = '\
        <form id="editor-form"> \
           <textarea class="editor-textarea">' + b64_to_utf8(data) + '</textarea> \
            <input type="hidden" id="sha" value=' + sha + '> \
            <input type="hidden" id="path" value=' + path + '> \
            <br> \
            <button id="update-content" class="btn btn-primary" type="button">Save</button> \
        </form>';
    $('#editor').html(editor_html);

    editor.init();
};

function addEditorTitle(volumeFileDom) {
    const volumeFilename = $(volumeFileDom).children("#volume-filename").text();
    const editorSection = $("#editor-section");
    editorSection.children("#editor-title").remove();
    editorSection.prepend('<p id="editor-title">' + '/' + volumeFilename + '</p>')
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


async function pushChanges(org, repo, branch, path, message, content, sha) {
    // console.log(org, repo, branch, path, message, content, sha);
    const ghClient = await getGHClient();
    const response = await ghClient.request('PUT /repos/{owner}/{repo}/contents/{path}', {
        owner: org,
        repo: repo,
        path: path,
        message: message,
        content: utf8_to_b64(content),
        sha: sha,
        branch: branch
    })

    return response;
};

async function updateContent(editorForm) {
    const path = $(editorForm).children("#path").val();
    const sha = $(editorForm).children("#sha").val();
    const content = editor.getValue();

    var commit_message = prompt("Commit message", "update " + path);

    const response = await pushChanges(window.gh_org, window.gh_repo, window.repo_branch, path, commit_message, content, sha);

    if (response['status'] == 200) {
        alert("Changes saved!");
        const new_sha = response['data']['content']['sha'];
        $(editorForm).children("#sha").val(new_sha);
        listFiles(window.gh_org, window.gh_repo, window.repo_branch);
    } else {
        alert("Changes cannot be saved");
    }
};

$(document).ready(function () {
    $("body").delegate("#update-content", "click", function () {
        updateContent(this.parentElement);
    });
});