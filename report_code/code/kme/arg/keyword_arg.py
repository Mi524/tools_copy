# -*- coding: utf-8 -*-
"""
关键词参数, 关键词是所有匹配的最基本核心
"""
from __future__ import unicode_literals

import six

from .rule_range_arg import s_range_arg
from ..nlp import lemmatize, word_tokenize
from ..result import Results
from ..rule import SeqRule
from ..text.text import Text


class SingleKeywordArg(object):
    """
    关键词参数, 仅能匹配一个单词. 用作内部使用
    """

    def __init__(self, is_raw, word):
        """
        初始化 Keyword 对象

        :param is_raw: 是否是匹配没有 lemmatize 的词条
        :param word: 待匹配的关键词
        """
        self.is_raw = is_raw
        self.word = word

    def match(self, text):
        """
        匹配对象进行文本的关键词匹配.

        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回空的 Results
        """
        if self.is_raw:  # 原始匹配
            results = text.raw_map.get(self.word)
        else:
            results = text.word_map.get(self.word)

        if results is None:  # 没有结果返回空
            return Results()
        else:
            return results


@six.python_2_unicode_compatible
class KeywordArg(object):
    """
    关键词参数, 匹配一个单词. 单词会通过分词操作.
    """

    def __init__(self, config, is_raw, word, beg_index, end_index):
        """
        初始化 Keyword 对象

        :param config: 存储配置信息的对象
        :param is_raw: 是否是匹配没有 lemmatize 的词条
        :param word: 待匹配的关键词
        :param beg_index: 当前 arg 在语法文本中的起始下标 (闭区间)
        :param end_index: 当前 arg 在语法文本中的结束下标 (开区间)
        """
        self.config = config
        self.is_raw = is_raw

        # 语言类别
        language = config.get('language', 'en')
        # 是否分词时附加词性
        with_pos = config.get('with_pos', False)
        # 分词是否是字级别的
        char_level = config.get('char_level', False)

        # 判断是否要 lemmatize
        if self.is_raw:
            if with_pos:
                self.words = [
                    x[0] for x in word_tokenize(
                        language,
                        word,
                        with_pos=with_pos,
                        char_level=char_level,
                    )
                ]
            else:
                self.words = list(word_tokenize(
                    language,
                    word,
                    with_pos=with_pos,
                    char_level=char_level,
                ))
        else:
            if with_pos:
                self.words = [
                    lemmatize(language, x[0]) for x in word_tokenize(
                        language,
                        word,
                        with_pos=with_pos,
                        char_level=char_level,
                    )
                ]
            else:
                self.words = [
                    lemmatize(language, x) for x in word_tokenize(
                        language,
                        word,
                        with_pos=with_pos,
                        char_level=char_level,
                    )
                ]
        if len(self.words) == 0:
            raise ValueError('KeywordArg needs ONE word at least', word)

        self.beg_index = beg_index
        self.end_index = end_index

    def __str__(self):
        return 'KeywordArg(is_raw={}, words=[{}], beg_index={}, end_index={})'.format(
            self.is_raw,
            ', '.join(self.words),
            self.beg_index,
            self.end_index
        )

    def match(self, text):
        """
        匹配对象进行文本的关键词匹配.

        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回空的 Results
        """
        assert isinstance(text, Text), 'text is not Text object'
        if len(self.words) == 1:
            ska = SingleKeywordArg(self.is_raw, self.words[0])
            return ska.match(text)
        else:  # > 1 的情况
            args = [SingleKeywordArg(self.is_raw, x) for x in self.words]
            seq_rule = SeqRule(self.config, self.beg_index, self.end_index, s_range_arg, *args)
            return seq_rule.match(text)
