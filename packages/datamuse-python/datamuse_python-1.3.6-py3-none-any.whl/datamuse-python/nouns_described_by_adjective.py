import requests
from bs4 import BeautifulSoup
import json
import warnings

def nouns_described_by_adjective(adjective):
    warnings.warn("This Function can also be called by calling 'getNounsMatchingAdjective' which also uses the same argument.")
    """
    Retrieves nouns commonly described by the given adjective using the Datamuse API.
    
    Args:
        adjective (str): The adjective to find associated nouns for.
        
    Returns:
        str: A space-separated string of associated nouns.
    """
    url = f"https://api.datamuse.com/words?rel_jja={adjective}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)



def getNounsMatchingAdjective(adjective):
    """
    Retrieves nouns commonly described by the given adjective using the Datamuse API.
    
    Args:
        adjective (str): The adjective to find associated nouns for.
        
    Returns:
        str: A space-separated string of associated nouns.
    """
    url = f"https://api.datamuse.com/words?rel_jja={adjective}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


