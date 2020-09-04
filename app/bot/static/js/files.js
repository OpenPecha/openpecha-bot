function getFileDOM(file, org, repo, branch) {
    return '<a href="#" id="volume-file"> \
                <span id="volume-filename">' + file['name'] + '</span> \
                <input type="hidden" id="org" value=' + org + '> \
                <input type="hidden" id="repo" value=' + repo + '> \
                <input type="hidden" id="branch" value=' + branch + '> \
                <input type="hidden" id="download-url" value=' + file['download_url'] + '> \
                <input type="hidden" id="path" value=' + file['path'] + '> \
                <input type="hidden" id="sha" value=' + file['sha'] + '> \
            </a>'
};

function getFiles(content, org, repo, branch) {
    var files = '<ul class="list-group overrides">';
    var file_icon = '<span class="oi oi-file"></span>';
    for (file of content) {
        files += '<li class="list-group-item">' + file_icon + getFileDOM(file, org, repo, branch) + '</li>';
    };
    files += '</ul>';
    return files
};

function listFiles(org, repo, branch) {
    const repo_content_url = `https://api.github.com/repos/${org}/${repo}/contents?ref=${branch}`;
    return fetch(repo_content_url)
        .then(response => response.json())
        .then(content => {
            $('.repo-files').html(getFiles(content, org, repo, branch));
        })
};