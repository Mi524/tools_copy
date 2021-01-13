# -*- coding: utf-8 -*-
"""
用于处理/存储/管理文本的对象
"""
from __future__ import unicode_literals

from collections import defaultdict

import six

from .index import Index
from .term import Term
from ..nlp import lemmatize, sent_tokenize, word_tokenize
from ..result import Result, Results


@six.python_2_unicode_compatible
class Text(object):
    """
    文档对象, 所有文档生成为文档对象后再进行处理.
    为了提高效率会生成两个关键词及其 Term 对象的映射表:
    """

    def __init__(self, config, paragraphs, word_list):
        """
        初始化 Text 对象

        :param config: 存储配置信息的对象
        :param paragraphs: 段落数据, 格式为:
            * paragrapshs = [sentence_1, sentence_2, ...]
            * sentence_n = [word_1, word_2, ...]
            * word_n = (paragraph_index, sentence_index, word_index, word)
        :param word_list: 词条列表, 直接分词后的词的列表 (每个词都没有进行 lemmatize)
        """
        self.config = config
        self.paragraphs = paragraphs
        self.word_list = tuple(word_list)

        # 存放没有 lemmatize 的词条映射
        self.raw_map = defaultdict(Results)
        # 存放已经 lemmatize 的词条映射
        self.word_map = defaultdict(Results)
        bias = 0
        for para in self.paragraphs:
            for sent in para:
                for word in sent:
                    # 生成阶段 bias 都是 0
                    result = Result(self.config, self.word_list, word.index, word.index, bias)
                    # 添加
                    self.raw_map[word.raw_word].add(result)
                    self.word_map[word.word].add(result)

    @classmethod
    def new(cls, text, config):
        """
        所有文档都分为整篇、段落、句子、词这几个维度。
        1. 段落使用 \n 分割
        2. 句子使用标点符号分割

        :param text: 初始化文本. 段落使用 \t 分割, 句子使用 。！……分割, 词使用空格分割
        :param config: 存储配置信息的对象
        """
        # 存储的格式为:
        # paragrapshs = [sentence_1, sentence_2, ...]
        # sentence_n = [word_1, word_2, ...]
        # word_n = (paragraph_index, sentence_index, word_index, word)
        if not text:
            word_list = []
            paragraphs = [[[]]]
        else:
            language = config['language']
            # 最多 5000 个字符 (默认), 多了会出错
            text = text[:config.get('max_text_length', 5000)]
            offset, i_para, i_sent, i_word = 0, 0, 0, 0
            word_list = []
            paras = []
            for paragraph in text.split('\n'):
                sents = []
                for sentence in sent_tokenize(language, paragraph):
                    words = []
                    for word_n_pos in word_tokenize(
                            language,
                            sentence,
                            with_pos=config.get('with_pos', False),  # 是否附带词性
                            char_level=config.get('char_level', False)  # 是否是字级别
                    ):
                        if config.get('with_pos', False):
                            word, pos = word_n_pos
                        else:
                            word = word_n_pos
                            pos = None  # 无词性

                        if word in (' ', '　'):  # 全角和半角的空格
                            continue

                        word_list.append(word)
                        if word:
                            index = Index(i_para, i_sent, i_word, offset)
                            # 词条会进行 lemmatize
                            raw_word = word
                            word = lemmatize(language, word)
                            term = Term(index, word, raw_word, pos)
                            words.append(term)
                            i_word += 1
                            offset += 1
                    if words:
                        sents.append(words)
                        i_word = 0
                        i_sent += 1
                if sents:
                    paras.append(sents)
                    i_word = 0
                    i_sent = 0
                    i_para += 1

            paragraphs = paras

        return Text(config, paragraphs, word_list)

    def slice_by_index(self, beg_index, end_index, **kwargs):
        """
        通过起始结束位置来切片文本

        :param beg_index: 起始 Index 对象
        :param end_index: 结束 Index 对象
        :param including_beg: 是否包含 beg_index 所指的 word, 默认为 True
        :param including_end: 是否包含 end_index 所指的 word, 默认为 False
        :return: 返回指定范围的文本, 并以 Text 对象的形式返回.
        """
        assert beg_index <= end_index, 'invalid range'
        assert isinstance(beg_index, Index), 'beg_index is not a Index object'
        assert isinstance(end_index, Index), 'end_index is not a Index object'
        including_beg = kwargs.get('including_beg', True)
        including_end = kwargs.get('including_end', False)

        tmp_paras = []
        for para in self.paragraphs:
            tmp_sents = []
            for sent in para:
                tmp_words = []
                for word in sent:
                    if including_beg and beg_index > word.index:
                        continue
                    elif (not including_beg) and beg_index >= word.index:
                        continue
                    elif including_end and word.index > end_index:
                        continue
                    elif (not including_end) and word.index >= end_index:
                        continue
                    tmp_words.append(word)
                if tmp_words:
                    tmp_sents.append(tmp_words)
            if tmp_sents:
                tmp_paras.append(tmp_sents)

        return Text(tmp_paras)

    def slice(self, **kwargs):
        """
        获取部分切片信息

        :param para_range: 段落的起始/结束 index, 支持负数的定位方式
        :param sent_range: 句子的起始/结束 index, 支持负数的定位方式
        :param word_range: 词的起始/结束 index, 支持负数的定位方式
        :return: 返回指定范围的文本, 并以 Text 对象的形式返回.
        """
        # 设定的最大范围, 理论上不会超过
        max_range = 1000000
        para_range = kwargs.get('para_range', (0, max_range))
        sent_range = kwargs.get('sent_range', (0, max_range))
        word_range = kwargs.get('word_range', (0, max_range))
        if para_range is None and sent_range is None and word_range is None:
            return self

        tmp_paras = []
        for para in self.paragraphs.__getslice__(*para_range):
            tmp_sents = []
            for sent in para.__getslice__(*sent_range):
                tmp_words = []
                for word in sent.__getslice__(*word_range):
                    tmp_words.append(word)
                tmp_sents.append(tmp_words)
            tmp_paras.append(tmp_sents)

        return Text(tmp_paras)

    def text(self):
        """
        获取所有数据, 以 Text 对象的形式

        :return: 返回 "段落-句子-词" 结构的数据, 无数据返回空数组
        """
        return self.paragraphs

    def __str__(self):
        if self.empty():
            return 'Text(empty)'
        else:
            para_strs = []
            for para in self.paragraphs:
                sent_strs = []
                for sent in para:
                    word_strs = []
                    for word in sent:
                        word_strs.append(word.word)
                    sent_strs.append('[{}]'.format(' '.join(word_strs)))
                para_strs.append('{{{}}}'.format(', '.join(sent_strs)))
            return 'Text([{}])'.format(', '.join(para_strs))

    def __eq__(self, other):
        return self.text() == other.text()

    def __len__(self):
        return len(self.word_list)

    def empty(self):
        """
        是否是空 Text
        """
        return True if self.paragraphs == [[[]]] else False

    @property
    def beg_index(self):
        """
        文本的起始 index
        """
        if self.empty():
            return Index(9999, 9999, 9999, 0)
        else:
            return self.paragraphs[0][0][0].index

    @property
    def end_index(self):
        """
        文本的结束 index
        """
        if self.empty():
            return Index(-1, -1, -1, 0)
        else:
            return self.paragraphs[-1][-1][-1].index

    def del_append(self, other):
        """
        在当前 Text 后面附上 other 文档. 会先判断文本是不是连贯的, 不连贯的无操作.

        :param other: 其他 Text 对象
        """
        # TODO: 需要添加关键词映射表, 先判断这个函数是不是有用, 我先改个名字
        assert isinstance(other, self.__class__)
        self_index = self.end_index
        other_index = other.beg_index
        if other_index.offset != self_index.offset + 1:  # 不合法
            return

        # 需要考虑的只包括相邻的 paragraph
        if other_index.i_para == self_index.i_para:  # 需要拼接
            if other_index.i_sent == self_index.i_sent:
                self.paragraphs[-1][-1].extend(other.text()[0][0])
                # 其余的 sentence
                self.paragraphs[-1].extend(other.text()[0][1:])
            else:
                self.paragraphs[-1].extend(other.text()[0])
            # 其余的 paragraph
            self.paragraphs.extend(other.text()[1:])
        else:  # 直接添加在最后
            self.paragraphs.extend(other.text())
