# -*- coding: utf-8 -*-

from functools import wraps
from os.path import abspath, dirname
from collections import Counter
import math

def to_string(bytes_or_str):
    """receive str or unicode and always return string"""
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode("utf-8")
    else:
        value = bytes_or_str
    return value

def cached_property(getter):
    """
    Decorator that converts a method into memorized property.The decorator
    works as expected only for classes with attribute '__dict__' and immutable
    properties
    """
    @wraps(getter)
    def decorator(self):
        key = "_cached_property_" + getter.__name__

        if not hasattr(self, key):
            setattr(self, key, getter(self))

        return getattr(self, key)

    return property(decorator)

def unicode_compatible(cls):
    """
    Decorator for unicode compatible classes. Method '__unicode__' has to be
    implemented to work decorator as expected
    """
    cls.__str__ = lambda self: self.__unicode__().encode("utf-8")

    return cls

def get_stop_words(language):
    stop_words_path = abspath(dirname(__file__)) + "/data/stopwords/{0}.txt".format(language)
    # print(stop_words_path)
    stop_words_data = []
    try:
        with open(stop_words_path, 'rb') as file:
            for line in file:
                stop_words_data.append(line.splitlines()[0].strip())
    except IOError as e:
        raise LookupError("Stop-words are not availale for language {0}".format(language))
    return frozenset(to_string(word) for word in stop_words_data if word)


def read_stop_words(filename):
     with open(filename, "rb") as open_file:
         return parse_stop_words(open_file.read())

def parse_stop_words(data):
    return frozenset(w.rstrip() for w in to_string(data).splitlines() if w)

def compute_tf(document_words):
    '''
    document_words: list
    '''
    tf_values = map(Counter, document_words)
    docset_tf  = []
    for document_tf in tf_values:
        metrics = {}
        all_tf = sum(document_tf.values())
        for term, tf in document_tf.items():
            metrics[term] = tf / all_tf
        docset_tf.append(metrics)
    return docset_tf

def compute_idf(document_words):
    idf_metrics = {}
    document_count = len(document_words)
    for document_word in document_words:
        for term in document_word:
            if term not in idf_metrics:
                number_doc = sum(1 for doc in document_words
                                 if term in doc )
                idf_metrics[term] = math.log(
                    document_count / (1 + number_doc)
                )
                if idf_metrics[term] < 0:
                    idf_metrics[term] = 0.0
    return idf_metrics


def cosine_similarity(sentence_words1, sentence_words2, tf1, tf2, idf_metrics):
    """
        We compute idf-modified-cosine(sentence1, sentence2) here.
        It's cosine similarity of these two sentences (vectors) A, B computed as cos(x, y) = A . B / (|A| . |B|)
        Sentences are represented as vector TF*IDF metrics.

        :param sentence_word1:
            tuple or list of words, for example Sentence.words in nlp_sum.my_sum.models.sentence
        :param sentence2:
            tuple or list of words, for example Sentence.words in nlp_sum.my_sum.models.sentence
        :type tf1: dict
        :param tf1:
            Term frequencies of words from document in where 1st sentence is.
        :type tf2: dict
        :param tf2:
            Term frequencies of words from document in where 2nd sentence is.
        :type idf_metrics: dict
        :param idf_metrics:
            Inverted document metrics of the sentences. Every sentence is treated as document for this algorithm.
        :rtype: float
        :return:
            Returns -1.0 for opposite similarity, 1.0 for the same sentence and zero for no similarity between sentences.
        """
    unique_words1 = frozenset(sentence_words1)
    unique_words2 = frozenset(sentence_words2)
    common_words = unique_words1 & unique_words2

    numerator = sum(tf1[term] * tf2[term] * idf_metrics[term]**2
                    for term in common_words)
    denominator1 = sum(
        ((tf1[term] * idf_metrics[term])**2 for term in unique_words1)
    )
    denominator2 = sum(
        ((tf2[term] * idf_metrics[term])**2 for term in unique_words2)
    )

    if denominator1 > 0 and denominator2 > 0:
        return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2))
    else:
        return 0.0


if __name__ == "__main__":
    stop_words = get_stop_words("chinese")
    print(stop_words)
