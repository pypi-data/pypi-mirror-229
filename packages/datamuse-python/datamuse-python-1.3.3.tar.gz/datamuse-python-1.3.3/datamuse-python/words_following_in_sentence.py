import requests
from bs4 import BeautifulSoup
import json
import warnings

def words_following_in_sentence(base_word, prefix):
    warnings.warn("This Function can also be called by calling 'getWordThatFollowWord' which also uses the same argument.")
    """
    Retrieves words that follow 'base_word' in a sentence and start with the specified 'prefix' using the Datamuse API.
    
    Args:
        base_word (str): The base word to find following words for.
        prefix (str): The desired prefix for following words.
        
    Returns:
        str: A space-separated string of following words.
    """
    url = f"https://api.datamuse.com/words?lc={base_word}&sp={prefix}*"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




def getWordThatFollowWord(base_word, prefix):
    """
    Retrieves words that follow 'base_word' in a sentence and start with the specified 'prefix' using the Datamuse API.
    
    Args:
        base_word (str): The base word to find following words for.
        prefix (str): The desired prefix for following words.
        
    Returns:
        str: A space-separated string of following words.
    """
    url = f"https://api.datamuse.com/words?lc={base_word}&sp={prefix}*"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

