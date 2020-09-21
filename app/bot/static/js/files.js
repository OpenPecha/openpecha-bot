function getFileDOM(file, org, repo, branch) {
    return '<a href="#" id="volume-file"> \
                <span id="volume-filename">' + file['name'] + '</span> \
                <input type="hidden" id="sha" value=' + file['sha'] + '> \
                <input type="hidden" id="path" value=' + file['path'] + '> \
            </a>'
};

function getFiles(content, org, repo, branch) {
    var files = '<ul class="list-group overrides">';
    var file_icon = '<span class="oi oi-file"></span>';
    for (var file of content) {
        files += '<li class="list-group-item">' + file_icon + getFileDOM(file, org, repo, branch) + '</li>';
    };
    files += '</ul>';
    return files
};

export async function listFiles(org, repo, branch) {
    const repo_content_url = `https://api.github.com/repos/${org}/${repo}/contents?ref=${branch}`;
    const response = await fetch(repo_content_url);
    const content = await response.json();
    window.gh_org = org;
    window.gh_repo = repo;
    window.repo_branch = branch;
    $('.repo-files').html(getFiles(content, org, repo, branch));
};
