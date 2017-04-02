import requests
import nltk
from random_words import RandomWords
from config import *
import numpy as np



def _get_nouns(tagged_words):
    nouns = [word for word, pos in tagged_words if pos[:2] == 'NN']
    if len(nouns) > 0:
        return nouns
    else:
        return None

def _select_rhyme(uniform=True):
    nums = [0, 1, 2]
    if uniform:
        p = [1.0/3, 1.0/3, 1.0/3]
    else:
        p = [.8, .2, 0.0]
    return np.random.choice(nums, size=1, p=p)[0]

def _tokenize(sentence):
    return nltk.word_tokenize(sentence)

def _pos_tag(tokens):
    return nltk.pos_tag(tokens)

def _get_top_n(words, n=20):
    # print words
    top_n = sorted(words, key=lambda x: x['score'], reverse=True)

    return top_n[:n]

def _get_related_word(nouns):
    if len(nouns) == 0:
        nouns = [RandomWords().random_word()]
    noun = np.random.choice(nouns, size=1).tolist()[0]
    payload = {'rel_trg' : noun}
    related_words = requests.get(datamuse_url, payload).json()
    related_words = [word for word in related_words if 'score' in word and word['score'] > 0]
    if len(related_words) == 0:
        related_words = [{'word' : RandomWords().random_word(), 'score' : 1}]
    return related_words

def _get_rhymes(input_word, rhyme_type, topics=None, repeat=False):
    all_rhymes = []

    if rhyme_type == 0:
        payload = {'rel_rhy' : input_word}
        if topics is not None:
            payload['topics'] = ','.join(topics)
        try: 
            rhymes = requests.get(datamuse_url, params=payload).json()
            all_rhymes.extend([word for word in rhymes if 'score' in word and word['score'] > 0])
            

    elif rhyme_type == 1:
        payload = {'rel_nry' : input_word}
        if topics is not None:
            payload['topics'] = ','.join(topics)
        try:
            slant = requests.get(datamuse_url, params=payload).json()
            all_rhymes.extend([word for word in slant if 'score' in word and word['score'] > 0])

    elif rhyme_type == 2:
        payload = {'rel_hom' : input_word}
        if topics is not None:
            payload['topics'] = ','.join(topics)
        try:
            homophones = requests.get(datamuse_url, params=payload).json()
            all_rhymes.extend([word for word in homophones if 'score' in word and word['score'] > 0])

    if len(all_rhymes) == 0 and topics is not None and not repeat:
        if rhyme_type == 0:
            rhyme_type = 1
        else:
            rhyme_type = 0
        all_rhymes = _get_rhymes(input_word, rhyme_type, repeat=True)

    return all_rhymes

def _normalize_words(words):
    total = sum([int(word['score']) for word in words])*1.0
    normalized_list = [(word['word'], int(word['score'])/total) for word in words]
    return normalized_list

def _choose_word(words, p):
    return np.random.choice(words, size=1, p=p).tolist()[0]

def _get_preceding_word(word, rhyme_type, rhyme=None, rhyme_weight = 10):
    preceding_words = []

    if not rhyme is None:
        if rhyme_type == 0:
            payload = {'rel_rhy' : rhyme, 'rel_bgb' : word}
            rhymes = requests.get(datamuse_url, params=payload).json()
            for rhyme_word in rhymes:
                if 'score' in rhyme_word and rhyme_word['score'] > 0:
                    rhyme_word['score'] *= rhyme_weight
                    preceding_words.append(rhyme_word)
        elif rhyme_type == 1:
            payload = {'rel_nry' : rhyme, 'rel_bgb' : word}
            slant = requests.get(datamuse_url, params=payload).json()
            for slant_word in slant:
                if 'score' in slant_word and slant_word['score'] > 0:
                    slant_word['score'] *= rhyme_weight
                    preceding_words.append(slant_word)
        elif rhyme_type == 2:
            payload = {'rel_hom' : rhyme, 'rel_bgb' : word}
            homophones = requests.get(datamuse_url, params=payload).json()
            for homo_word in homophones:
                if 'score' in homo_word and homo_word['score'] > 0:
                    homo_word['score'] *= rhyme_weight
                    preceding_words.append(homo_word)

    payload = {'rel_bgb' : word}
    non_rhymes = requests.get(datamuse_url, params=payload).json()

    for non_rhyme in non_rhymes:
        if 'score' in non_rhyme and non_rhyme['score'] > 0:
            preceding_words.append(non_rhyme)
    #print preceding_words

    return preceding_words

def _count_syllables(word):
    if word.count(' ') > 0:
        total = 0
        for n in word.split(' '):
            lowercase = n.lower()
            if lowercase in cmud:
                total += max([len([y for y in x if y[-1].isdigit()]) for x in cmud[lowercase]])
        return total
    lowercase = word.lower()
    if lowercase in cmud:
        total=max([len([y for y in x if y[-1].isdigit()]) for x in cmud[lowercase]])
        if type(total) is not int:
            return 0
        return total
    return 0

def get_response(sentence, length=None, start_word=None):
    
    tokens = _tokenize(sentence)
    tagged_words = _pos_tag(tokens)
    nouns = _get_nouns(tagged_words)
    not_punc_sentence = [word for (word, pos) in tagged_words if pos[0].isalpha()]
    # old = ' '.join(not_punc_sentence)

    if length is None:
        length = 0
        for word in not_punc_sentence:
            length += _count_syllables(word)
    if length > 15:
        length = 15
    
    if start_word is not None:
        next_word = start_word
    else:
        last_word = not_punc_sentence.pop()

        rhymes = _get_rhymes(last_word, _select_rhyme(uniform=False), topics=nouns)
        if len(rhymes) == 0:
            rhymes = _get_related_word(nouns)
        # print rhymes
        top_n = _get_top_n(rhymes)
        rhyming_words = _normalize_words(top_n)
        words = [word[0] for word in rhyming_words]
        p = [word[1] for word in rhyming_words]

        next_word = _choose_word(words, p)
    
    syllables = _count_syllables(next_word)

    response = [next_word]
    while syllables < length:
        if not_punc_sentence:
            word_to_rhyme = not_punc_sentence.pop()
        else:
            word_to_rhyme = None

        pre_words = _get_preceding_word(response[0], _select_rhyme(), rhyme=word_to_rhyme)
        if len(pre_words) == 0:
            pre_words = _get_related_word(nouns)

        top_n = _get_top_n(pre_words)
        preceding_words = _normalize_words(top_n)
        words = [word[0] for word in preceding_words]
        p = [word[1] for word in preceding_words]

        next_word = _choose_word(words, p)
        syllables += _count_syllables(next_word)
        response.insert(0, next_word)

    return ' '.join(response)
