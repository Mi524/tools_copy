# -*- coding: utf-8 -*-
"""
规则过滤器语法分析
"""
from __future__ import unicode_literals

import re

from ..filter import RuleFilter


class RuleFilterSyntax(object):
    """
    规则过滤器的语法规则为:

        !filt(目标规则, 限制范围 1, 限制规则 1, ...)

    其中,
        * 目标规则是指要被过滤的规则
        * 限制范围: 表示对目标规则进行限制的限制范围, 其修饰的是紧邻其后的限制规则
        * 限制规则: 表示对目标规则进行限制的规则, 其一定要配合限制范围一起操作

    限制范围/限制规则是成对出现, 当只有其中一个时为 "非法语法", 会报错处理.
    限制范围/限制规则可以多个出现, 表示对目标规则的限制 (串行). 例如:

        !filt($seq(@d4, "turn", "on"),
              @[d3, 0, 0], $or("not", "can't", "won't", "wouldn't")
        )
    """
    re_match = re.compile(r'!filt\(')

    @classmethod
    def ignore_space(cls, text, index):
        """
        忽略 "空" 字符, 空字符为:

            * 空格
            * 制表符
            * 换行符

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 返回不是 "空" 字符的索引
        """
        while index < len(text):
            if text[index] in '\t\n\r ':
                index += 1
                continue
            break
        return index

    def __init__(self, config, beg_index, arg_index):
        self.config = config
        self.beg_index = beg_index
        self.arg_index = arg_index

    @classmethod
    def match(cls, config, text, index, *args, **kwargs):
        """
        规则过滤器的语法匹配

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回 RestrictRule 对象, 不成功返回 None
        """
        if text.startswith('!f', index):
            m = cls.re_match.match(text, index)
            if m:
                beg_index, arg_index = m.span(0)
                return cls(config, beg_index, arg_index)
            else:
                raise ValueError('invalid rule_filter')

    def assemble(self, args, end_index):
        """
        将头信息和参数拼装成为完整的规则

        :param args: 参数列表
        :param end_index: 结束索引号
        :return: 返回对应的 RuleFilter 对象, 如果不成功报错
        """
        return RuleFilter(self.config, self.beg_index, end_index, *args)
