function fetchFileContent(download_url) {
    return fetch(download_url)
        .then(response => response.text())
        .then(text => {
            console.log(text);
            $(".editor-textarea").text(text)
        });
};


$(document).ready(function () {
    $("body").delegate("#volume-file", "click", function () {
        var download_url = $(this).children("#file-download-url").val();
        fetchFileContent(download_url);
    });

    //code here...
    var editor = new CodeMirror.fromTextArea($(".editor-textarea")[0], {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        theme: "dracula"
    });

    var text = editor.getValue()


});