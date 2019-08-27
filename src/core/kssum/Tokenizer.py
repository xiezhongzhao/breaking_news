# -*- coding: utf-8 -*-

import sys
import re
import nltk
import jieba
import logging

from kssum.utils import to_string
jieba.setLogLevel(logging.INFO)


def chinese_word_segment(unicode_str):
    """jieba cut result is a generator"""
    return list(jieba.cut(unicode_str))


def chinese_representation(text):
    sentence_delimiters = ['?', '!', '？', '！',
                           '。', '……', '…', '\n']
    delimiters = set([to_string(item) for item in sentence_delimiters])
    text = to_string(text)
    delimiters_idx = [-1]
    res, idx_list, words_list = [], [], []

    for idx, token in enumerate(text):
        if token in delimiters:
            if idx < len(text) - 1 and text[idx+1] == '”':
                delimiters_idx.append(idx+1)
            else:
                delimiters_idx.append(idx)

    if len(delimiters_idx) == 1:
        res.append(text)
        idx_list.append([0, len(text)])
        words_list.append(chinese_word_segment(text))
        return [res, idx_list, words_list]

    for start_idx, end_idx in zip(delimiters_idx[:-1], delimiters_idx[1:]):
        if text[end_idx] in ['?', '？']:
            continue
        else:
            sent = text[start_idx+1:end_idx+1]
            res.append(sent)
            words_list.append(chinese_word_segment(sent))
            idx_list.append([start_idx+1, end_idx+1])
    return res, idx_list, words_list


def english_representation(text):
    delimiters = ['?', '!', '？', '！', '.',
                  '。', '……', '…', '\n']
    text = to_string(text)
    delimiters_idx = [-1]
    res, idx_list, words_list = [], [], []

    for idx, token in enumerate(text):
        if token in delimiters:
            if idx < len(text) - 1 and text[idx+1] == '"':
                delimiters_idx.append(idx+1)
            else:
                delimiters_idx.append(idx)

    if len(delimiters_idx) == 1:
        res.append(text)
        idx_list.append([0, len(text)])
        words_list.append(nltk.word_tokenize(text))
        return [res, idx_list, words_list]

    for start_idx, end_idx in zip(delimiters_idx[:-1], delimiters_idx[1:]):
        if text[end_idx] in ['?', '？']:
            continue
        else:
            sent = text[start_idx+1:end_idx+1]
            res.append(sent)
            idx_list.append([start_idx+1, end_idx+1])
            words_list.append(nltk.word_tokenize(sent))
    return res, idx_list, words_list



if __name__ == '__main__':
    cnstring ='北京时间4月19日，勇士客场132-105击败了快船。在勇士与快船的这轮系列赛中，由于上一场比赛勇士在领先了31分的情况下被快船翻盘最终输掉了比赛。而这一场比赛，来到快船的主场，勇士同样在第三节领先了对手高达31分，但是这一次，勇士没有再重蹈上一场的覆辙，最终大胜对手。'
    enstring = '''The Sydney-based woman, who chose to remain anonymous, said the door of the bathroom would 'always shake' when two people were getting frisky behind it. She said passengers can only join the club if they met on the plane and decided to have sex, rather than just partners who were bored during the flight.'''
    print(chinese_representation(cnstring))
    idxtuple = chinese_representation(cnstring)[1][0]
    print(cnstring[idxtuple[0]: idxtuple[1]])

    print(english_representation(enstring))
    enidxtuple = english_representation(enstring)[1][0]
    print(enstring[enidxtuple[0]: enidxtuple[1]])
