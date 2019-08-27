# -*- coding: utf-8 -*-

from kssum._summarizer import AbstractSummarizer

import math
import numpy
from numpy.linalg import norm
from nltk.stem import SnowballStemmer
from kssum.utils import compute_tf, compute_idf
from functools import reduce


class SubmodularSummarizer(AbstractSummarizer):

    _stop_words = frozenset()

    def __init__(self, language="chinese", stemmer_or_not=False):
        if language.startswith("en") and stemmer_or_not:
            super(SubmodularSummarizer, self).__init__(
                language,
                SnowballStemmer("english").stem
            )
        else:
            super(SubmodularSummarizer, self).__init__(language)

    @property
    def stop_words(self):
        return self._stop_words

    @stop_words.setter
    def stop_words(self, words):
        self._stop_words = frozenset(map(self.normalize_word, words))

    def __call__(self, document, sents_limit=None, words_limit=None, Lambda=0.5, beta=0.1):
        assert Lambda < 1, "Lambda must be in interval [0, 1]"
        assert beta < 1, "beta must be in interval [0, 1]"
        return self.greedy(document, sents_limit, words_limit, Lambda, beta)

    def _filter_out_stop_words(self, words):
        return [word for word in words if word not in self._stop_words]

    def _normalize_words(self, words):
        words = map(self.normalize_word, words)
        return self._filter_out_stop_words(words)

    def _normalize_words_list(self, wordslist):
        words_list = [self._normalize_words(tmp) for tmp in wordslist]
        return words_list

    def _create_dictionary(self, wordslist):
        """
        Creates mapping key = word, value = row index
        """
        wordslist = self._normalize_words_list(wordslist)
        words = reduce(lambda x, y: x + y, wordslist)
        unique_words = frozenset(words)
        return dict((word, idx) for idx, word in enumerate(unique_words))

    def _create_tfidf_matrix(self, words_list, dictionary):
        sentences_count = len(words_list)
        self.sent_cout = sentences_count
        words_in_every_sent = self._normalize_words_list(words_list)
        tf_value_every_sent = compute_tf(words_in_every_sent)
        idf_value = compute_idf(words_in_every_sent)
        words_count = len(dictionary)
        # create matrix |unique_words|x|sentences| filled with zeroes
        matrix = numpy.zeros((words_count, sentences_count))
        for idx, words_sent in enumerate(words_in_every_sent):
            for word in words_sent:
                if word in dictionary:
                    row = dictionary[word]
                    matrix[row, idx] = tf_value_every_sent[idx][word] * idf_value[word]
        return matrix

    def _create_sim_matrix(self, words_list, tfidf_matrix):
        similarity_matrix = numpy.zeros((self.sent_cout, self.sent_cout))

        if tfidf_matrix.shape[1] == self.sent_cout:
            tfidf_matrix = tfidf_matrix.T

        for sent_num1 in range(self.sent_cout):
            for sent_num2 in range(sent_num1):
                similarity_matrix[sent_num1, sent_num2] = self._cosSim(tfidf_matrix[sent_num1, :],
                                                                       tfidf_matrix[sent_num2, :])

        similarity_matrix = similarity_matrix + similarity_matrix.T + numpy.eye(self.sent_cout)
        return similarity_matrix

    def _row_similarity_sum(self, similarity_matrix):
        # subtract the similarity with sentence self
        return sum(similarity_matrix - numpy.eye(self.sent_cout))

    def _submodular_L(self, summary_idx_set, row_similarity_sum,
                      similarity_matrix, sent_idx, alpha):
        # sent_idx represents the sentence which will be added to summary
        # to calculate its score
        score = 0.0

        for sent_idx_doc in range(self.sent_cout):
            # sent_idx will be added to summary
            if sent_idx_doc == sent_idx:
                continue
            sum_similarity = 0
            for sent_idx_summary in summary_idx_set:
                if sent_idx_doc != sent_idx_summary:
                    sum_similarity += similarity_matrix[sent_idx_doc, sent_idx_summary]

                if sent_idx != -1:
                    # add the sentence to summary
                    sum_similarity += similarity_matrix[sent_idx_doc, sent_idx]

            score_final = min(row_similarity_sum[sent_idx_doc] * alpha, sum_similarity)
            score = score + score_final
        return score

  # calculate the redundancy
    def _submodular_R(self, summary_idx_set, similarity_matrix, sent_idx):
        score = 0.0
        for summary_idx in summary_idx_set:
            score = score + similarity_matrix[summary_idx, sent_idx]

        return -score

    def judge_sentence(self, sentence):
        sentence_delimiters = ['?', '!', ';', '？', '！', '。',
                               '；', '……', '…', '.', ',']
        for sep in sentence_delimiters:
            if sep in sentence:
                return True
        return False

    def judge_sent_rule(self, sentence):
        sentence_delimiters = ['?', '!', ';', '？', '！', '。',
                               '；', '……', '…', '.', ',']
        delimiters_number = 0
        for sep in sentence_delimiters:
            if sep in sentence:
                delimiters_number += 1

        if (sentence.endswith('说。') or sentence.endswith('表示。')) and \
           delimiters_number == 1:
            return False
        return True

    def judge_redundancy_sent(self, sent_words, doc_representation, summary_idx_set):
        '''
        sentence: document sentences
        '''
        textlist, idxlist, wordslist = doc_representation
        sent_words_set = [wordslist[idx] for idx in summary_idx_set]
        for words_sent in sent_words_set:
            sent_words = set(sent_words)
            sentence_words = set(words_sent)
            same_words = sent_words.intersection(sentence_words)
            if len(same_words) / len(sent_words) > 0.65 or \
               len(same_words) / len(sentence_words) > 0.65:
                return True
        return False

    def greedy(self, document, sents_limit=None, words_limit=None, Lambda=0.5, beta=0.1):
        textlist, idxlist, wordslist = self.get_doc_representation(document)
        dictionary = self._create_dictionary(wordslist)
        if textlist:
            union_list = list(zip(textlist, idxlist, wordslist))
        else:
            union_list = [('', 0, 'none')]

        if not dictionary:
            return ()

        summary = []
        summary_idx_set = []
        summary_word_count = 0

        tfidf_matrix = self._create_tfidf_matrix(wordslist, dictionary)
        similarity_matrix = self._create_sim_matrix(wordslist, tfidf_matrix)
        row_similarity_sum = self._row_similarity_sum(similarity_matrix)

        alpha = (1 / self.sent_cout) * 10
        sent_chosen = [False for i in range(self.sent_cout)]



        if not words_limit:

            while True:
                max_increment_score = float("-inf")
                max_sent_idx = -1
                init_score = self._submodular_L(summary_idx_set, row_similarity_sum, similarity_matrix, -1, alpha)

                for sent_idx in range(self.sent_cout):
                    sent_len = self._get_sentence_length(textlist[sent_idx])
                    if not sent_chosen[sent_idx] and sent_len > 8 and self.judge_sentence(textlist[sent_idx]) and \
                       not self.judge_redundancy_sent(wordslist[sent_idx], [textlist, idxlist, wordslist], summary_idx_set) and self.judge_sent_rule(textlist[sent_idx]):
                        L_score = self._submodular_L(summary_idx_set, row_similarity_sum,
                                                     similarity_matrix, sent_idx, alpha)
                        R_score = self._submodular_R(summary_idx_set, similarity_matrix, sent_idx)
                        increment_score = Lambda * L_score + (1 - Lambda) * R_score - Lambda * init_score
                        increment_score = increment_score / math.pow(sent_len, beta)

                        if increment_score > max_increment_score:
                            max_increment_score = increment_score
                            max_sent_idx = sent_idx

                if max_sent_idx == -1:
                    break

                sent_chosen[max_sent_idx] = True
                summary_idx_set.append(max_sent_idx)
                if len(summary_idx_set) == sents_limit:
                    break

        else:
            while True:
                max_increment_score = float('-inf')
                max_sent_idx = -1
                init_score = self._submodular_L(summary_idx_set, row_similarity_sum, similarity_matrix, -1, alpha)
                for sent_idx in range(self.sent_cout):
                    sent_len = self._get_sentence_length(textlist[sent_idx])
                    if not sent_chosen[sent_idx] and (sent_len + summary_word_count) < words_limit and sent_len > 8 and self.judge_sentence(textlist[sent_idx]) and not self.judge_redundancy_sent(wordslist[sent_idx], [textlist, idxlist, wordslist], summary_idx_set) and self.judge_sent_rule(textlist[sent_idx]):
                        L_score = self._submodular_L(summary_idx_set, row_similarity_sum,
                                                     similarity_matrix, sent_idx, alpha)
                        R_score = self._submodular_R(summary_idx_set, similarity_matrix, sent_idx)
                        increment_score = Lambda * L_score + (1 - Lambda) * R_score - Lambda * init_score
                        increment_score = increment_score / math.pow(sent_len, beta)

                        if increment_score > max_increment_score:
                            max_increment_score = increment_score
                            max_sent_idx = sent_idx

                if max_sent_idx == -1:
                    break
                summary_word_count += self._get_sentence_length(textlist[max_sent_idx])
                if summary_word_count > words_limit:
                    break
                sent_chosen[max_sent_idx] = True
                summary_idx_set.append(max_sent_idx)

        finallist = [union_list[choose] for choose in summary_idx_set]
        return finallist
