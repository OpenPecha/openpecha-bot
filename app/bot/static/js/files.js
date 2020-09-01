function getFileDOM(file) {
    return '<a href="#" id="volume-file"> \
                <span id="volume-filename">' + file['name'] + '</span> \
                <input type="hidden" id="download-url" value=' + file['download_url'] + '> \
                <input type="hidden" id="path" value=' + file['path'] + '> \
                <input type="hidden" id="sha" value=' + file['sha'] + '> \
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