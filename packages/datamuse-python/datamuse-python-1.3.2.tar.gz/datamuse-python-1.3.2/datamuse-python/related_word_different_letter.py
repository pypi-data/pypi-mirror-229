import requests
from bs4 import BeautifulSoup
import json

def related_word_different_letter(word1, word):
    url = f"https://api.datamuse.com/words?ml={word1}&sp={word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


