import requests
from bs4 import BeautifulSoup
import json

def related_word(word, letters, word2):
    url = f"https://api.datamuse.com/words?sp={word1}{letters}{word2}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


