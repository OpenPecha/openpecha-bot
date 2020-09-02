async function fetchFileContent(volumeFileDom) {
    const download_url = $(volumeFileDom).children("#download-url").val();
    const response = await fetch(download_url);
    const content = await response.text();
    return content;
};

async function prepareTextEditorForm(volumeFileDom) {
    const text = await fetchFileContent(volumeFileDom);
    const path = $(volumeFileDom).children("#path").val();
    const sha = $(volumeFileDom).children("#sha").val();
    console.log(path);
    console.log(sha);
    const editor_html = '\
        <form id="editor-form"> \
            <textarea class="editor-textarea">' + text + '</textarea> \
            <input type="hidden" id="path" value=' + path + '> \
            <input type="hidden" id="sha" value=' + sha + '> \
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