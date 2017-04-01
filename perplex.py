import requests
import nltk
import enchant
from random_words import RandomWords
from config import *


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

def _get_rhymes(word, topics=None, n=20):
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

    top_n = sorted(all_rhymes, key=lambda x: x['score'], reverse=True)[:n]
    # print top_n
    return top_n

def _normalize_rhymes(rhyming_words):
    total = sum([int(word['score']) for word in rhyming_words])*1.0
    normalized_list = [(word['word'], int(word['score'])/total) for word in rhyming_words]
    return normalized_list

def _get_last_word(tagged_words):
    not_punc_list = [(word, pos) for (word, pos) in tagged_words if pos.isalpha()]
    return not_punc_list[-1][0]

def get_response(sentence):
    global previous_topic
    
    tokens = _tokenize(sentence)
    tagged_words = _pos_tag(tokens)
    nouns = _get_nouns(tagged_words)
    
    last_word = _get_last_word(tagged_words)
    rhyming_words = _normalize_rhymes(_get_rhymes(last_word, nouns))
    
    

    return rhyming_words