from mining_tool.__main__ import main


def test_mid():
    main([
        '--discourse', 'https://discourse.diasporafoundation.org',
        '--exp', 'data/diaspora_discourse/issues.csv',
    ])

def test_large():
    main([
        '--discourse', 'https://discuss.python.org',
        '--exp', 'data/python_discourse/issues.csv',
    ])