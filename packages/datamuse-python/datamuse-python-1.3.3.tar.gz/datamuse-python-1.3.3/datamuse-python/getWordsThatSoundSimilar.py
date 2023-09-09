import requests
from bs4 import BeautifulSoup
import json
import warnings

def getWordsThatSoundSimilar(word):
    warnings.warn("This Function can also be called by calling 'getWordWithDifferentPrefix' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?sl={word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)