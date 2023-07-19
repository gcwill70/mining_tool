from mining_tool.__main__ import main


def test_small():
    main([
        '--github', 'JacobSPalmer/repo_issues_dc',
        '--exp', 'data/repo_issues_dc/issues.csv',
        '--freq', 'data/repo_issues_dc/issues_freq.csv',
    ])

def test_mid():
    main([
        '--github', 'Wilfred/difftastic',
        '--exp', 'data/difftastic/issues.csv',
        '--freq', 'data/difftastic/issues_freq.csv',
    ])