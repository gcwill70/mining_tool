from mining_tool.__main__ import main


def test_small():
    main([
        '--github', 'JacobSPalmer/repo_issues_dc',
        '--imp', 'data/repo_issues_dc/issues.csv',
        '--comments-imp', 'data/repo_issues_dc/issues/issue',
        '--comments-exp', 'data/repo_issues_dc/issues/issue',
    ])

def test_mid():
    main([
        '--github', 'Wilfred/difftastic',
        '--imp', 'data/difftastic/issues.csv',
        '--comments-imp', 'data/difftastic/issues/issue',
        '--comments-exp', 'data/difftastic/issues/issue',
    ])