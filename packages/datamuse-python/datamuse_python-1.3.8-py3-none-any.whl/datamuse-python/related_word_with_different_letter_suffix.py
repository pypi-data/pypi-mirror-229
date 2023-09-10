import requests
from bs4 import BeautifulSoup
import json
import warnings

def related_word_with_different_letter_suffix(word1, word):
    warnings.warn("This Function can also be called by calling 'getWordWithDifferentSuffix' which also uses the same argument.")
    """
    Retrieves words related to 'word1' that have a specific 'word' suffix using the Datamuse API.
    
    Args:
        word1 (str): The base word to find related words for.
        word (str): The desired suffix for related words.
        
    Returns:
        str: A space-separated string of related words.
    """
    url = f"https://api.datamuse.com/words?ml={word1}&sp={word}*"
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


def getWordWithDifferentSuffix(word1, word):
    """
    Retrieves words related to 'word1' that have a specific 'word' suffix using the Datamuse API.
    
    Args:
        word1 (str): The base word to find related words for.
        word (str): The desired suffix for related words.
        
    Returns:
        str: A space-separated string of related words.
    """
    url = f"https://api.datamuse.com/words?ml={word1}&sp={word}*"
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

