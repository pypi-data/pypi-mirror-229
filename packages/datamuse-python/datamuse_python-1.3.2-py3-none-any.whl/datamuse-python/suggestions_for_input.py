import requests
from bs4 import BeautifulSoup
import json

def suggestions_for_input(word1):
    url = f"https://api.datamuse.com/sug?s={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


