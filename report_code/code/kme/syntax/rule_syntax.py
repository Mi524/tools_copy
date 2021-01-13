# -*- coding: utf-8 -*-
"""
RULE 的基类
"""
from __future__ import unicode_literals

import re

from ..rule import ArgRule, BagRule, OrRule, OrdRule, SeqRule


class RuleSyntax(object):
    re_match = re.compile(r'\$(\w+)[\t\r\n ]*\(')
    # 规则递归的层级, 用来计算规则是否完全结束
    rule_count = 0
    rule_name_map = {
        'or': OrRule,
        'ord': OrdRule,
        'bag': BagRule,
        'seq': SeqRule,
        'arg': ArgRule,
    }

    @classmethod
    def match(cls, config, text, index, *args, **kwargs):
        """
        规则的语法匹配, 依据 text[index] 判断是否是规则.

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回 起始索引号， 结束索引号， 规则名称
        """
        if text[index] == '$':
            m = cls.re_match.match(text, index)
            if m:
                beg_index, arg_index = m.span(0)
                rule_name = m.group(1)
                rule_cls = cls.rule_name_map[rule_name]
                return cls(config, beg_index, arg_index, rule_cls)
            else:
                raise ValueError('invalid rule', text[index:])
        else:
            return None

    def __init__(self, config, beg_index, arg_index, rule_cls):
        self.config = config
        self.beg_index = beg_index
        self.arg_index = arg_index
        self.rule_cls = rule_cls

    def assemble(self, args, end_index):
        """
        将头信息和参数拼装成为完整的规则

        :param args: 参数列表
        :param end_index: 结束索引号
        :return: 返回对应的 Rule 对象, 如果不成功报错
        """
        return self.rule_cls(self.config, self.beg_index, end_index, *args)
