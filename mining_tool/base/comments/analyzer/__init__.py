# https://github.com/ponder-lab/GitHub-Issue-Classifier
import re
from string import punctuation

import spacy
from joblib import load
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download on first run
# import nltk
# nltk.download('wordnet')
# nltk.download('stopwords')
# nltk.download('omw-1.4')
# nltk.download('punkt')


from spacy.lang.en import English
eng = spacy.load('en_core_web_sm')

parser = English()

stop_words = list(punctuation) + ["'s","'m","n't","'re","-","'ll",'...', "/"] + stopwords.words('english')


def get_lemma(item: str):
    return WordNetLemmatizer().lemmatize(item)

def codeReplace(comment: str):
    return re.sub('```([^`]*)```|`([^`]*)`', 'CODE', comment or '')

def expand(comment: str):
    expanded = []
    for line in comment.splitlines():
        line = line.strip('\n').strip('\t')
        if line:
            expanded.append(line)
    return expanded

def processLine(c: str):
    # Replace \n newline character and \t tabs
    c = c.replace('\n', '')
    c = c.replace('\t', '')

    # Array to store all processed string tokens
    processed_tokens = []

    # Parse them into Token using spacy parser
    parsed_line = parser(c)

    # If the line starts with ">" (markdown for quote), return QUOTE token for line
    # as this line is a quoted line.
    if(str(parsed_line[0]) == ">"):
        return "QUOTE"

    # For each token/word in the line that, tokenize the remaining URL/SCREEN_NAME
    # And also filter out words that are in the stop_words list.
    for token in parsed_line:
        if token.orth_.isspace():
            continue
        elif str(token) == "CODE":
            processed_tokens.append("CODE")
        elif token.like_url:
            processed_tokens.append('URL')
        elif token.orth_.startswith('@'):
            processed_tokens.append('SCREEN_NAME')
        elif str(token) not in stop_words:
            processed_tokens.append(get_lemma(token.lower_))

    # Return it as a string.
    return ' '.join(processed_tokens)

def getLines(comment):
    return expand(codeReplace(comment))

def classify_comment(comment):
    model = load("mining_tool/base/comments/models/comments_logisticRegression.model")
    vectorizer = load("mining_tool/base/comments/models/comments_logisticRegression.countVector")
    parsed = processLine(comment)
    test_vector = vectorizer.transform([parsed])
    return parsed, model.predict(test_vector)[0]

def get_utterances(comment):
    return tokenize.sent_tokenize(comment)

