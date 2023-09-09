import requests
from bs4 import BeautifulSoup
import json
import warnings

def rythming_word(word1):
    warnings.warn("This Function can also be called by calling 'getWordRythm' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?rel_rhy={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


def getWordRythm(word1):
    url = f"https://api.datamuse.com/words?rel_rhy={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)