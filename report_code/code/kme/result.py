# -*- coding: utf-8 -*-
"""
返回结果的存储对象
"""
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class Result(object):
    """
    单个结果的存储对象, 包含的主要是 Term 的队列.
    """

    def __init__(self, config, word_list, beg_index, end_index, bias):
        """
        :param config: 存储配置信息的对象
        :param word_list: 命中的原始词条列表 Text.word_list
        :param beg_index: 起始 Index 对象 (闭区间)
        :param end_index: 结束 Index 对象 (闭区间)
        :param bias: 偏离量, 在强制 concept 长度为 1 的场景中用来作为偏移值减去
        """
        self.config = config
        self.word_list = word_list
        self.beg_index = beg_index
        self.end_index = end_index
        self.bias = bias

    #修改 增加获取wordlist和 index 的方法
    def get_wordlist(self):
        return self.word_list

    def get_index(self,name):
        if name == 'beg_index':
            return self.beg_index
        elif name == 'end_index':
            return self.end_index
        else:
            raise ValueError("没有该属性{}".format(name))

    def __str__(self):
        return 'Result(text={0}, beg_index={1}, end_index={2}, bias={3})'.format(
            self.text,
            self.beg_index,
            self.end_index,
            self.bias,
        )

    def __len__(self):
        """
        会判断是否是把 concept 的结果算作长度 1

        :return: 返回依据 concept['force_concept_size_one'] 的长度
        """
        return self.end_index.offset - self.beg_index.offset + 1 - self.bias

    @staticmethod
    def zh_join(word_list):
        """
        针对中文进行 join, 逻辑为:
        1. 如果相邻两个字符中存在拉丁字母, 两者之间增加空格
        2. 否则不增加空格
<
        :param word_list: 待 join 的词的列表
        :return: 返回 join 后的词的列表
        """

        def is_latin(ch):
            o = ord(ch)
            if 0x0000 <= o <= 0x007F or 0x0080 <= o <= 0x00FF or 0x0100 <= o <= 0x017F \
                    or 0x0180 <= o <= 0x024F or 0x2C60 <= o <= 0x2C7F or 0xA720 <= o <= 0xA7FF \
                    or 0xAB30 <= o <= 0xAB6F or 0x1E00 <= o <= 0x1EFF or 0xFF00 <= o <= 0xFFEF \
                    or 0xFB00 <= o <= 0xFB4F or 0x0250 <= o <= 0x02AF or 0x1D00 <= o <= 0x1D7F \
                    or 0x1D80 <= o <= 0x1DBF:
                return True
            else:
                return False

        if len(word_list) == 1:
            return word_list[0]

        index = 1
        join_words = [word_list[0]]
        while index < len(word_list):
            prev = word_list[index - 1]
            curr = word_list[index]
            # 因为拉丁字母肯定会和中文分开, 所以只需要看最后一个字符和第一个字符就行
            if is_latin(prev[-1]) or is_latin(curr[0]):
                # 命中, 添加空格
                join_words.append(' ')
            join_words.append(curr)
            index += 1
        return ''.join(join_words)

    @property
    def text(self):
        language = self.config.get('language', 'en')
        if language == 'en':
            return ' '.join(self.word_list[self.beg_index.offset: self.end_index.offset + 1])
        elif language == 'zh':
            return self.zh_join(self.word_list[self.beg_index.offset: self.end_index.offset + 1])
        else:
            raise ValueError('invalid_language')

    @property
    def hit(self):
        """
        是否命中, 命中表示有匹配结果,
        """
        return self.end_index.offset >= self.beg_index.offset

    def overlap(self, other):
        """
        是否与 other 有重叠
        """
        return self.end_index.offset >= other.beg_index.offset \
               and other.end_index.offset >= self.beg_index.offset

    @property
    def matched_words(self):
        """
        返回匹配到的词列表, 实际上是:
        self.word_list[self.beg_index.offset: self.end_index.offset + 1]

        :return: 返回匹配到的词条
        """
        return self.word_list[self.beg_index.offset: self.end_index.offset + 1]


@six.python_2_unicode_compatible
class Results(object):
    """
    存放若干 Result 对象的对象 (自动去重). 同时包含一些好用的方法.
    """

    def __init__(self):
        self.result_set = set()

    def clean(self):
        """
        清空对象所包含的所有内容 (等效于初始化)
        """
        self.result_set.clear()

    def add(self, *element_list):
        """
        添加一个或多个 Result / Results

        :param element_list: 一个或多个 Result / Results 对象
        """
        for element in element_list:
            # Result 对象
            if isinstance(element, Result):
                self.result_set.add(element)
            # Results 对象
            elif isinstance(element, Results):
                self.result_set.update(element.result_set)
            else:
                continue

    def remove(self, element):
        """
        通过传递一个 Result / Results 对象来删除多个 Result

        :param element: Results / Result 对象
        """
        if isinstance(element, Result):
            self.result_set.discard(element)
        elif isinstance(element, Results):
            self.result_set.difference_update(element.result_set)

    def __str__(self):
        return 'Results([{}])'.format(', '.join([six.text_type(x) for x in self.result_set]))

    def __len__(self):
        return len(self.result_set)

    def __iter__(self):
        return self.result_set.__iter__()
