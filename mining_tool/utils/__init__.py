import glob

import nltk


def conform(data: dict, fields):
    ret = {}
    for field in fields:
        ret[field] = data[field] if field in data.keys() else None
    return ret

def transform(data: dict, mapping: dict):
    for old, new in mapping.items():
        data[new] = data.pop(old, None)
    return data

def find_file(path: str):
    paths = glob.glob(path)
    return sorted(paths, key=len)[0] if len(paths) > 0 else None

def setup():
    nltk.download('wordnet')
    nltk.download('stopwords')
    nltk.download('omw-1.4')
    nltk.download('punkt')