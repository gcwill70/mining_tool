from mining_tool.__main__ import main


def test_mid():
    main([
        '--discourse', 'https://discourse.diasporafoundation.org',
        '--imp', 'data/diaspora_discourse/issues_all.csv',
        '--comments-imp', 'data/diaspora_discourse/issues/issue',
        '--comments-exp', 'data/diaspora_discourse/issues/issue',
    ])