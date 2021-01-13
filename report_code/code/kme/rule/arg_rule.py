# -*- coding: utf-8 -*-
"""
参数规则 (概念名称或关键词), 因为对外 (用户接口) 必须是规则, 所以本质上是对 keyword_arg, concept_arg 的封装
"""
from __future__ import unicode_literals

from .base_rule import BaseRule


class ArgRule(BaseRule):
    """
    参数规则
    """

    def validate(self):
        """
        参数的合法性检验, 不合法抛出异常.

        1. 只支持一个参数
        2. 参数只能是 关键词 (KeywordArg) 或 概念 (ConceptArg)
        """
        # 1. 只支持一个参数
        if len(self.args) != 1:
            raise ValueError('ArgRule only support ONE argument')

        # 2. 参数类型限制
        supported_arg_names = ('KeywordArg', 'ConceptArg')
        arg_name = self.args[0].__class__.__name__
        if arg_name not in supported_arg_names:
            raise ValueError('ArgRule only support argument of types ({})'.format(
                ', '.join(supported_arg_names)
            ), arg_name)

    def match(self, text):
        """
        匹配对象进行文本的规则匹配

        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回 None
        """
        # 如果没有匹配到就返回一个空的 Results
        # 用来存放每个 arg 的匹配 Results
        match_arg = self.args[0]
        results = match_arg.match(text)

        return results
