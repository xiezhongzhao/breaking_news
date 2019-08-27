# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import attrgetter
import math

import re
import numpy
from numpy.linalg import norm

from kssum.utils import to_string, cached_property
from kssum.Tokenizer import chinese_representation, english_representation


def get_cn_sentence_length(sentence):
    """
    get the actual length of chinese sentence
    :para : Sentence()
    """
    # the length of ', NBA' should be two
    # the length of ',NBA' will be one
    # the same behavior as microsoft word
    chinese_word_pattern = re.compile(u"[\u4e00-\u9fa5。；，：“”（）、？《》]+",
                                      re.UNICODE)
    english_or_number_pattern = re.compile(u"[^\u4e00-\u9fa5\s。；，：“”（）、？《》]+",
                                           re.UNICODE)
    chinese_word_list = re.findall(chinese_word_pattern, sentence)
    english_or_number_list = re.findall(english_or_number_pattern, sentence)
    chinese_len = len(''.join(chinese_word_list))
    english_or_number_len = len(english_or_number_list)
    # 1 represents the '。'
    # return chinese_len + english_or_number_len + 1
    return chinese_len + english_or_number_len

def get_en_sentence_length(sentence):
    words_list = sentence.split()
    return len(words_list)

def null_stemmer(string):
    "Converts given string to unicode with lower letters."
    return to_string(string).lower()


class AbstractSummarizer(object):
    def __init__(self, language="chinese", stemmer=null_stemmer):
        if not callable(stemmer):
            raise ValueError("Stemmer should be a callable method")

        self._stemmer = stemmer
        self.language = language.lower()

        if self.language.startswith("en"):
            self._get_sentence_length = get_en_sentence_length
        if self.language.startswith("ch"):
            self._get_sentence_length = get_cn_sentence_length

    def __call__(self, input_document, words_count):
        raise NotImplementedError("The method should be overridden in subclass")

    def normalize_word(self, word):
        return self._stemmer(to_string(word).lower())

    def _cosSim(self, vector1, vector2):
        # both vector are row vectors
        vector1, vector2 = numpy.mat(vector1), numpy.mat(vector2)
        numerator = float(vector1 * vector2.T)
        denominator = norm(vector1) * norm(vector2)
        if denominator > 0:
            return numerator / denominator
        else:
            return 0.0

    def get_doc_representation(self, doc):
        '''
        doc: string
        '''
        if self.language.startswith('en'):
            return english_representation(doc)
        if self.language.startswith('ch'):
            return chinese_representation(doc)
