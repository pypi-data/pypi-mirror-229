from .beautify_json import beautify_json
from .nouns_described_by_adjective import nouns_described_by_adjective,getNounsMatchingAdjective
from .related_word_with_different_letter_prefix import related_word_with_different_letter_prefix, getWordWithDifferentPrefix
from .related_word_with_different_letter_suffix import related_word_with_different_letter_suffix, getWordWithDifferentSuffix
from .related_word_with_letters import related_word_with_letters, getWordWithCertainAmountOfLetters
from .rhyming_words_related_to_base_word import rhyming_words_related_to_base_word, getRhymingWords
from .rythming_word import rythming_word, getWordRythm
from .suggestions_for_input import suggestions_for_input, getWordSuggestions
from .words_following_in_sentence import words_following_in_sentence, getWordThatFollowWord
from .words_that_describe_adjectives import rwords_that_describe_adjectives, getWordThatDescribesAdjective
from .words_triggered_by_association import words_triggered_by_association, getWordTriggeredByAssociation
from .getAdjectivesByRelation import getAdjectiveByRelation
from .getWordSpelledSimilar import getWordSpelledSimilar
from .getWordsThatSoundSimilar import getWordsThatSoundSimilar
# Import other functions

__all__ = [
    'beautify_json', 'nouns_described_by_adjective','getNounsMatchingAdjective',
    'related_word_with_different_letter_prefix','getWordWithDifferentPrefix', 'related_word_with_different_letter_suffix','getWordWithDifferentSuffix',
    'related_word_with_letters','getWordWithCertainAmountOfLetters', 'rhyming_words_related_to_base_word','getRhymingWords', 'rythming_word','getWordRythm',
    'suggestions_for_input','getWordSuggestions', 'words_following_in_sentence','getWordThatFollowWord', 'rwords_that_describe_adjectives','getWordThatDescribesAdjective',
    'words_triggered_by_association','getWordTriggeredByAssociation','getAdjectiveByRelation','getWordSpelledSimilar','getWordsThatSoundSimilar'
    # List other functions here
]
