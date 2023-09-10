import requests
from bs4 import BeautifulSoup
import json
import warnings

def related_word_with_different_letter_prefix(word1, word):
    warnings.warn("This Function can also be called by calling 'getWordWithDifferentPrefix' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?ml={word1}&sp=*{word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)



def getWordWithDifferentPrefix(word1, word):
    url = f"https://api.datamuse.com/words?ml={word1}&sp=*{word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)