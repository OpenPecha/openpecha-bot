var tokenTypes = {
    bookTitle: "BookTitle",
    potiTitle: "PotiTitle",
    author: "Author",
    chapter: "Chapter",
    topic: "Text",
    subTopic: "SubText",
    pagination: "Pagination",
    citation: "Citation",
    correction: "Correction",
    errorCandidate: "ErrorCandidate",
    peydurma: "Peydurma",
    sabche: "Sabche",
    tsawa: "Tsawa",
    yigchung: "Yigchung",
    archaic: "Archaic"
}

CodeMirror.defineSimpleMode("hfml", {
    // The start state contains the rules that are intially used
    start: [
        // The regex matches the token, the token property contains the type
        { regex: /"\[.*?\]"|$)/, token: tokenTypes.pagination },
    ]
});