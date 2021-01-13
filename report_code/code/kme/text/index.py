# -*- coding: utf-8 -*-
"""
索引对象
"""
from __future__ import unicode_literals

from collections import namedtuple
import six

BaseIndex = namedtuple("MixIndex", ['i_para', 'i_sent', 'i_word', "offset"])


@six.python_2_unicode_compatible
class Index(BaseIndex):
    """
    存储索引的对象, 同时包含部分简便操作

    初始化参数包括:
    :param i_para: Term 所在段落的 index
    :param i_sent: Term 所在句子的 index
    :param i_word: Term 所在词的 index
    :param offset: Term 在文章中的偏移量
    """

    @property
    def psw_index(self):
        """
        返回包含 para, sent, word 的混合索引号
        """
        return self.i_para, self.i_sent, self.i_word

    def __eq__(self, other):
        return self.i_para == other.i_para \
               and self.i_sent == other.i_sent \
               and self.i_word == other.i_word \
               and self.offset == other.offset

    def __gt__(self, other):
        return self.psw_index > other.psw_index

    def __ge__(self, other):
        return self.psw_index >= other.psw_index

    def __lt__(self, other):
        return self.psw_index < other.psw_index

    def __le__(self, other):
        return self.psw_index <= other.psw_index

    def __str__(self):
        return 'Index({},{},{},{})'.format(
            self.i_para,
            self.i_sent,
            self.i_word,
            self.offset,
        )

    #修改，返回每个index的字典
    def to_dict(self):
        return {
            'i_para':self.i_para,
            'i_sent':self.i_sent,
            'i_word':self.i_word,
            'offset':self.offset
        }
