function getFileDOM(file) {
    return '<a href="#" id="volume-file"> \
                <span id="volume-filename">' + file['name'] + '</span> \
                <input type="hidden" id="file-download-url" name="download-url" value=' + file['download_url'] + '> \
                </a>'
};

function getFiles(content) {
    var files = '<ul class="list-group overrides">';
    var file_icon = '<span class="oi oi-file"></span>';
    for (file of content) {
        files += '<li class="list-group-item">' + file_icon + getFileDOM(file) + '</li>';
    };
    files += '</ul>';
    return files
};

function listFiles(repo_content_api_url) {
    return fetch(repo_content_api_url)
        .then(response => response.json())
        .then(content => {
            $('.repo-files').html(getFiles(content));
        })
};

function getAuthToken() {
    return fetch('/api/auth')
        .then(response => response.json())
        .then(data => { return data['token'] });
}

function pushChanges(text) {
    const token_string = getAuthToken();
    var oauthAuth = new GitHub({
        token: token_string
    });
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
    const download_url = $(volumeFileDom).children("#file-download-url").val();
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