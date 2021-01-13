# -*- coding: utf-8 -*-
"""
用于处理英文相关的自然语言工具
"""
from __future__ import unicode_literals

from nltk import download
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag as _pt
from nltk.tokenize import sent_tokenize as _st, word_tokenize as _wt


def prepare():
    """
    使用英文时的准备工作, 下载对应的模型文件
    """
    for model_name in ('universal_tagset', 'averaged_perceptron_tagger', 'punkt', 'wordnet'):
        download(model_name, quiet=True)


class NlpEng(object):
    """
    处理英文的 NLP 工具集
    """

    __WNL = WordNetLemmatizer()

    @classmethod
    def pos_tag(cls, words):
        """
        为输入的词的列表标定词性, 仅支持英文.

        :param words: 输入的词列表
        :return: 返回词和词性的列表, 词性采用 universal 方式:
            * ADJ: adjective (new, good, high, special, big, local)
            * ADP: adposition (on, of, at, with, by, into, under)
            * ADV: adverb (really, already, still, early, now)
            * CONJ: conjunction (and, or, but, if, while, although)
            * DET: determiner, article (the, a, some, most, every, no, which)
            * NOUN: noun (year, home, costs, time, Africa)
            * NUM: numeral (twenty-four, fourth, 1991, 14:24)
            * PRT: particle (at, on, out, over per, that, up, with)
            * PRON: pronoun (he, their, her, its, my, I, us)
            * VERB: verb (is, say, told, given, playing, would)
            * .: punctuation marks (. , ; !)
            * X: other (ersatz, esprit, dunno, gr8, univeristy)
        """
        return _pt(words, tagset='universal')

    @classmethod
    def sent_tokenize(cls, paragraph):
        """
        将一个段落分割成为句子

        :param paragraph: 段落文本
        :return: 返回分割完成后的句子列表
        """
        sentences = _st(paragraph)
        return sentences

    @classmethod
    def word_tokenize(cls, sentence, with_pos=False, char_level=False, **kwargs):
        """
        将一个句子分割成为词/标点. 词会自动小写

        :param sentence: 句子文本
        :param with_pos: 是否需要包含词性, 默认为 True
        :param char_level: 对英文没意义
        :return: 返回分割完成后的词的列表: 包含词性为 [(word, pos), (word, pos), ...]
        """
        words = []
        for word in _wt(sentence):
            if word:
                words.append(word)

        if with_pos:
            words_with_pos = [(x[0].lower(), x[1]) for x in cls.pos_tag(words)]
            return words_with_pos
        else:
            return [x.lower() for x in words]

    @classmethod
    def lemmatize(cls, word, pos=None):
        """
        依据词和词性简化词, 所有词均会变成小写.

        :param word: 词
        :param pos: 词性, 词性仅支持 名词/动词/形容词/副词, 其余返回小写的原文.
                    不包含该参数则计算词性
        :return: 返回简化后的词
        """
        if pos is None:
            pos = cls.pos_tag([word])[0][1]

        if pos == 'NOUN':
            word = cls.__WNL.lemmatize(word, pos='n')
        elif pos == 'VERB':
            word = cls.__WNL.lemmatize(word, pos='v')
        elif pos == 'ADJ':
            word = cls.__WNL.lemmatize(word, pos='a')
        elif pos == 'ADV':
            word = cls.__WNL.lemmatize(word, pos='r')

        return word.lower()
