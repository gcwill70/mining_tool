from mining_tool.__main__ import main


def test_small():
    main([
        '--comments-imp', 'data/repo_issues_dc/issues_utterances/issue',
        '--comments-categorize-exp', 'data/repo_issues_dc/issues_categorized/issue',
    ])

def test_mid():
    main([
        '--comments-imp', 'data/difftastic/issues_utterances/issue',
        '--comments-categorize-exp', 'data/difftastic/issues_categorized/issue',
    ])

def test_mid2():
    main([
        '--comments-imp', 'data/diaspora_discourse/issues_utterances/issue',
        '--comments-categorize-exp', 'data/diaspora_discourse/issues_categorized/issue',
    ])
    