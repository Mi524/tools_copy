# -*- coding: utf-8 -*-
"""
逻辑或规则
"""
from __future__ import unicode_literals

from .base_rule import BaseRule
from ..result import Results


class OrRule(BaseRule):
    """
    逻辑或规则是对所有规则的一个补充, 因为所有规则都是逻辑与 (参数之间), 所以添加一个逻辑或
    """

    def validate(self):
        """
        参数的合法性检验, 不合法抛出异常.

        1. 参数最少需要 2 个, 1 个没意义
        2. 参数可以是:
            1) 关键词 (KeywordArg)
            2) 概念 (ConceptArg)
            3) 规则 (ArgRule, BagRule, OrRule, OrdRule, SeqRule)
            4) 规则过滤器 (RuleFilter)
        """
        # 1. 参数最少需要 2 个
        if len(self.args) < 2:
            raise ValueError('OrRule needs TWO arguments at least')

        # 2. 参数类别限制
        for index, arg in enumerate(self.args):
            arg_name = arg.__class__.__name__
            if arg_name not in self.__class__.default_supported_arg_names:
                raise ValueError('OrRule only support argument of types ({})'.format(
                    ', '.join(self.__class__.default_supported_arg_names)
                ), index, arg_name)

    def match(self, text):
        """
        匹配对象进行文本的规则匹配

        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回 None
        """
        # 如果没有匹配到就返回一个空的 Results
        results = Results()
        # 用来存放每个 arg 的匹配 Results
        for arg in self.args:
            arg_results = arg.match(text)
            if len(arg_results) > 0:
                results.add(arg_results)

        return results
