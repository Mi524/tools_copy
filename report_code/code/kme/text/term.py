# -*- coding: utf-8 -*-
"""
存储单词 (对于中文而言是词) 的对象
"""
from __future__ import unicode_literals

from collections import namedtuple
import six

BaseTerm = namedtuple("BaseTerm", ['index', 'word', 'raw_word', 'pos'])


@six.python_2_unicode_compatible
class Term(BaseTerm):
    """
    用于存储的富信息 (段落号, 句子号, 词号等) 的存储单元


    初始化参数包括:
    :param index: Index 对象
    :param word: 词条本身
    :param raw_word: 原始词条, 没有 lemmatize 的词条
    :param pos: 词条词性, 词性包括:
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

    def __str__(self):
        return 'Term(word={}, raw_word={}, pos={}, index={})'.format(
            self.word,
            self.raw_word,
            self.pos,
            self.index,
        )

    def __eq__(self, other):
        return self.index == other.index \
               and self.word == other.word \
               and self.raw_word == other.raw_word \
               and self.pos == other.pos
