import numpy as np
from nltk.tokenize import word_tokenize

all_vectors = []
selected_vectors = []

def get_vocab(data):
    vocab = []

    for sent in data:
        x = word_tokenize(sent)
        sentence = [w.lower() for w in x if w.isalpha() and len(w) > 2]
        for word in sentence:
            if word not in vocab:
                vocab.append(word)
    return vocab

def vectorize(vocab, answer):
    vector = np.zeros(len(vocab), int)
    for word in answer.split(" "):
        if word.lower() in vocab:
            vector[vocab.index(word.lower())] += 1
    return vector
