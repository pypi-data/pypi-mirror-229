import requests
import json
import bs4 as BeautifulSoup
import warnings

# Functions from beautify_json.py
def beautify_json(data):
    """
    Beautifies JSON data by adding indentation for improved readability.
    
    Args:
        data (str): The JSON data to be beautified.
        
    Returns:
        str: Beautified JSON data.
    """
    # Parse the JSON data into a Python dictionary
    data_dict = json.loads(data)

    # Convert the dictionary back to JSON with indentation for readability
    beautified_json = json.dumps(data_dict, indent=4)

    # Return the beautified JSON
    return beautified_json


# Functions from getAdjectivesByRelation.py
def getAdjectiveByRelation(word1, word):
    url = f"https://api.datamuse.com/words?rel_jjb={word1}&topics={word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

# Functions from getWordSpelledSimilar.py
def getWordSpelledSimilar(word):
    url = f"https://api.datamuse.com/words?sp={word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

# Functions from getWordsThatSoundSimilar.py
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

# Functions from my_library.py
# Functions from nouns_described_by_adjective.py
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




# Functions from related_word_with_different_letter_prefix.py
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

# Functions from related_word_with_different_letter_suffix.py
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



# Functions from related_word_with_letters.py
def related_word_with_letters(word1, letters, word2):
    warnings.warn("This Function can also be called by calling 'getWordWithCertainAmountOfLetters' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?sp={word1}{letters}{word2}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




def getWordWithCertainAmountOfLetters(word1, letters, word2):
    url = f"https://api.datamuse.com/words?sp={word1}{letters}{word2}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




# Functions from rhyming_words_related_to_base_word.py
def rhyming_words_related_to_base_word(base_word, rhyming_word):
    warnings.warn("This Function can also be called by calling 'getRhymingWords' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?ml={base_word}&rel_rhy={rhyming_word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)



def getRhymingWords(base_word, rhyming_word):
    url = f"https://api.datamuse.com/words?ml={base_word}&rel_rhy={rhyming_word}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




# Functions from rythming_word.py
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

# Functions from suggestions_for_input.py
def suggestions_for_input(word1):
    warnings.warn("This Function can also be called by calling 'getWordSuggestions' which also uses the same argument.")
    url = f"https://api.datamuse.com/sug?s={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)



def getWordSuggestions(word1):
    url = f"https://api.datamuse.com/sug?s={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)



# Functions from words_following_in_sentence.py
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



# Functions from words_that_describe_adjectives.py
def rwords_that_describe_adjectives(word1):
    warnings.warn("This Function can also be called by calling 'getWordThatDescribesAdjective' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?rel_jib={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




def getWordThatDescribesAdjective(word1):
    url = f"https://api.datamuse.com/words?rel_jib={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




# Functions from words_triggered_by_association.py
def words_triggered_by_association(word1):
    warnings.warn("This Function can also be called by calling 'getWordTriggeredByAssociation' which also uses the same argument.")
    url = f"https://api.datamuse.com/words?rel_trg={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




def getWordTriggeredByAssociation(word1):
    url = f"https://api.datamuse.com/words?rel_trg={word1}"
    r = requests.get(url)
    print(url)

    soup = BeautifulSoup(r.content, 'html5lib')
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)




