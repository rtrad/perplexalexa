import requests
import nltk
import enchant
from random_words import RandomWords
from config import *
import numpy as np


def _get_nouns(tagged_words):
    nouns = [word for word, pos in tagged_words if pos[:2] == 'NN']
    if len(nouns) > 0:
        return nouns
    else:
        return False

def _tokenize(sentence):
    return nltk.word_tokenize(sentence)

def _pos_tag(tokens):
    return nltk.pos_tag(tokens)

def _get_top_n(words, n=20):
    return sorted(words, key=lambda x: x['score'], reverse=True)[:n]

def _get_rhymes(word, topics=None):
    all_rhymes = []

    payload = {'rel_rhy' : word}
    if topics is not None:
        payload['topics'] = ','.join(topics)
    rhymes = requests.get(datamuse_url, params=payload).json()
    all_rhymes.extend([word for word in rhymes if 'score' in word])

    payload = {'rel_nry' : word}
    if topics is not None:
        payload['topics'] = ','.join(topics)
    slant = requests.get(datamuse_url, params=payload).json()
    all_rhymes.extend([word for word in slant if 'score' in word])

    payload = {'rel_hom' : word}
    if topics is not None:
        payload['topics'] = ','.join(topics)
    homophones = requests.get(datamuse_url, params=payload).json()
    all_rhymes.extend([word for word in homophones if 'score' in word])

    payload = {'rel_cns' : word}
    if topics is not None:
        payload['topics'] = ','.join(topics)
    consonants = requests.get(datamuse_url, params=payload).json()
    all_rhymes.extend([word for word in consonants if 'score' in word])
    # print top_n
    return all_rhymes

def _normalize_words(words):
    total = sum([int(word['score']) for word in words])*1.0
    normalized_list = [(word['word'], int(word['score'])/total) for word in words]
    return normalized_list

def _choose_word(words, p):
    return np.random.choice(words, size=1, p=p)

def _get_preceding_word(word, rhyme=None):
    preceding_words = []

    if not rhymes is None:
        payload = {'rel_rhy' : word, 'rel_bgb' : rhyme}
        rhymes = requests.get(datamuse_url, params=payload).json()
        preceding_words.extend([word for word in rhymes if 'score' in word])

        payload = {'rel_nry' : word, 'rel_bgb' : rhyme}
        slant = requests.get(datamuse_url, params=payload).json()
        preceding_words.extend([word for word in slant if 'score' in word])

        payload = {'rel_hom' : word, 'rel_bgb' : rhyme}
        homophones = requests.get(datamuse_url, params=payload).json()
        preceding_words.extend([word for word in homophones if 'score' in word])

        payload = {'rel_cns' : word, 'rel_bgb' : rhyme}
        consonants = requests.get(datamuse_url, params=payload).json()
        preceding_words.extend([word for word in consonants if 'score' in word])

    if len(preceding_words) == 0:
        payload = {'rel_bgb' : word}
        preceding_words = requests.get(datamuse_url, params=payload).json

    return preceding_words

def get_response(sentence, length=8):
    tokens = _tokenize(sentence)
    tagged_words = _pos_tag(tokens)
    nouns = _get_nouns(tagged_words)

    not_punc_sentence = [(word, pos) for (word, pos) in tagged_words if pos.isalpha()]
    last_word = not_punc_sentence.pop()

    top_n = _get_top_n(_get_rhymes(last_word, nouns))
    rhyming_words = _normalize_words(top_n)
    words = [word[0] for word in rhyming_words]
    p = [word[1] for word in rhyming_words]

    response = [_choose_word(words, p)]
    for i in range(0,length):
        top_n = _get_top_n(_get_preceding_word(response[0], not_punc_sentence.pop()))
        preceding_words = _normalize_words(top_n)
        words = [word[0] for word in preceding_words]
        p = [word[1] for word in preceding_words]

        response.insert(0, _choose_word(words, p))

    return ' '.join(response)
