function lanuchEditor(text) {
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
        theme: "dracula"
    });

    var text = editor.getValue();
};

function fetchFileContent(download_url) {
    return fetch(download_url)
        .then(response => response.text())
        .then(lanuchEditor)
};


$(document).ready(function () {
    $("body").delegate("#volume-file", "click", function () {
        const download_url = $(this).children("#file-download-url").val();
        console.log(download_url);
        fetchFileContent(download_url);
    });
});