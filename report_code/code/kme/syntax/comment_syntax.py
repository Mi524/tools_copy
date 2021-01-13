# -*- coding: utf-8 -*-
"""
注释语法分析, 直接干掉就行
"""
from __future__ import unicode_literals

import re

import six


@six.python_2_unicode_compatible
class CommentSyntax(object):
    """
    评论语法分析, 以 # 开始的当前行部分全为注释
    """

    re_comment = re.compile(r'#([^\n]*)(\n|$)')

    @classmethod
    def match(cls, config, text, index, *args, **kwargs):
        """
        依据 text[index] 判断是否是注释

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回注释对象, 不成功返回 None
        """
        if text[index] == '#':
            m = cls.re_comment.match(text, index)
            if m:
                comment = m.group(0)
                beg_index, end_index = m.span(0)
                return CommentSyntax(config, comment, beg_index, end_index)
            else:
                raise ValueError('invalid comment', text[index:])

    def __init__(self, config, comment, beg_index, end_index):
        self.config = config
        self.comment = comment
        self.beg_index = beg_index
        self.end_index = end_index

    def __str__(self):
        return 'CommentSyntax(comment={}, beg_index={}, end_index={})'.format(
            self.comment, self.beg_index, self.end_index
        )
