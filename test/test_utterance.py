from mining_tool.__main__ import main


def test_small():
    main([
        '--comments-imp', 'data/repo_issues_dc/issues/issue',
        '--comments-utterances-exp', 'data/repo_issues_dc/issues_utterances/issue',
    ])

def test_mid():
    main([
        '--comments-imp', 'data/difftastic/issues/issue',
        '--comments-utterances-exp', 'data/difftastic/issues_utterances/issue',
    ])

def test_mid2():
    main([
        '--comments-imp', 'data/diaspora_discourse/issues/issue',
        '--comments-utterances-exp', 'data/diaspora_discourse/issues_utterances/issue',
    ])