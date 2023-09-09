import requests
from bs4 import BeautifulSoup
import json

def words_triggered_by_association(word1):
    url = f"https://api.datamuse.com/words?rel_trg={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


