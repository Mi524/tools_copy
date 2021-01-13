# -*- coding: utf-8 -*-
"""
概念过滤器, 过滤指定概念所有结果的过滤器
"""
from __future__ import unicode_literals

import six

from ..result import Results


@six.python_2_unicode_compatible
class ConceptFilter(object):
    """
    概念过滤, 可以多条存放在指定规则中.
    """
    supported_arg_names = (
        'ArgRule', 'BagRule', 'OrRule', 'OrdRule', 'SeqRule',
        'RuleFilter',
        'KeywordArg', 'ConceptArg',
    )

    def __init__(self, config, beg_index, end_index, *args):
        """
        初始化 Restrict 对象

        :param config: 包含配置信息的对象
        :param beg_index: 当前规则在语法文本中的起始下标 (闭区间)
        :param end_index: 当前规则在语法文本中的结束下标 (开区间)
        :param args: 概念过滤器的参数列表
        """
        self.config = config
        self.beg_index = beg_index
        self.end_index = end_index
        self.args = args
        self.validate()

    def __str__(self):
        return 'ConceptFilter(args=[{}])'.format(
            ', '.join([six.text_type(x) for x in self.args]),
        )

    def validate(self):
        """
        参数的合法性检验, 不合法抛出异常.

        1. 参数个数必须是 2
        2. 第 1 个参数必须是过滤范围 (FilterRangeArg)
        3. 第 2 个参数可以是:
            1) 规则 (ArgRule, BagRule, OrRule, OrdRule, SeqRule)
            2) 规则过滤器 (RuleFilter)
            3) 关键词 (keywordArg) 和概念 (ConceptArg)
        """
        # 1. 参数至少要 2 个
        if len(self.args) != 2:
            raise ValueError('ConceptFilter needs TWO arguments exactly')

        # 2. 第 1 个参数必须是规则范围
        if self.args[0].__class__.__name__ != 'FilterRangeArg':
            raise ValueError('The first argument of ConceptFilter must be FilterRangeArg')

        # 3. 第 2 个参数类别限制
        arg_name = self.args[1].__class__.__name__
        if arg_name not in self.__class__.supported_arg_names:
            raise ValueError('ConceptFilter only support argument of types ({})'.format(
                ', '.join(self.__class__.supported_arg_names)
            ), arg_name)

    def filter(self, text, target_results):
        """
        对已经匹配的结果进行限制过滤, 滤除不合规范的结果

        :param text: 原文 Text 对象
        :param target_results: 目标结果, Concept 的所有结果
        :return: 返回滤除后的合规范结果
        """
        filter_range = self.args[0]
        filter_rule = self.args[1]

        filter_results = filter_rule.match(text)
        ret_results = Results()
        for target_result in target_results:
            # 没有被过滤则加进去
            if not filter_range.filter(target_result, filter_results):
                ret_results.add(target_result)

        return ret_results
