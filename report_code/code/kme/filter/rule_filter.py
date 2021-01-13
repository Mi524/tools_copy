# -*- coding: utf-8 -*-
"""
过滤, 可以对匹配结果的 前/后/中 三个部位进行匹配结果的过滤
"""
from __future__ import unicode_literals

import six

from ..result import Results


@six.python_2_unicode_compatible
class RuleFilter(object):
    """
    规则过滤, 可以多条存放在指定规则中.
    """
    supported_arg_names = (
        # rule
        'ArgRule', 'BagRule', 'OrRule', 'OrdRule', 'SeqRule',
        # filter
        'RuleFilter',
        # arg
        'KeywordArg', 'ConceptArg',
    )

    def __init__(self, config, beg_index, end_index, *args):
        """
        初始化 Restrict 对象

        :param config: 包含配置信息的对象
        :param beg_index: 当前规则在语法文本中的起始下标 (闭区间)
        :param end_index: 当前规则在语法文本中的结束下标 (开区间)
        :param args: 规则过滤器的参数列表
        """
        self.config = config
        self.beg_index = beg_index
        self.end_index = end_index
        self.args = args
        self.validate()

    def __str__(self):
        return 'RuleFilter(args=[{}])'.format(
            ', '.join([six.text_type(x) for x in self.args]),
        )

    def validate(self):
        """
        参数的合法性检验, 不合法抛出异常.

        1. 参数个数必须是 >= 3 的
        2. 第 1 个参数必须是目标规则
        3. 第 2 个及以后参数必须是过滤范围 (FilterRangeArg) 和 规则/过滤器成对出现, 规则/过滤器包括:
            1) 规则 (ArgRule, BagRule, OrRule, OrdRule, SeqRule)
            2) 规则过滤器 (RuleFilter)
            3) 关键词 (keywordArg) 和概念 (ConceptArg)
        """
        # 1. 参数至少要 2 个
        if len(self.args) < 3:
            raise ValueError('RuleFilter needs THREE arguments exactly')

        # 2. 第 1 个参数必须属于规则范围
        arg_name = self.args[0].__class__.__name__
        if arg_name not in self.__class__.supported_arg_names:
            raise ValueError('RuleFilter only support argument of types ({})'.format(
                ', '.join(self.__class__.supported_arg_names)
            ), arg_name)

        # 3. 要成对出现
        index = 1
        if len(self.args) % 2 != 1:
            raise ValueError('FilterRangeArg and filter rule are not PAIRWISE')

        while index < len(self.args):
            arg = self.args[index]
            # 3.1. 第一个必须是规则范围
            if arg.__class__.__name__ != 'FilterRangeArg':
                raise ValueError('The first argument in PAIR must be FilterRangeArg')
            index += 1

            arg = self.args[index]
            # 3.2. 第二个必须属于规则范围
            arg_name = arg.__class__.__name__
            if arg_name not in self.__class__.supported_arg_names:
                raise ValueError('RuleFilter only support argument of types ({})'.format(
                    ', '.join(self.__class__.supported_arg_names)
                ), index, arg_name)
            index += 1

    def match(self, text):
        """
        对已经匹配的结果进行限制过滤, 滤除不合规范的结果

        :param text: 原文 Text 对象
        :return: 返回滤除后的合规范结果
        """
        target_rule = self.args[0]

        filter_results_list = []
        # 一个 range 一个 rule, 按顺序成对出现
        for filter_range, filter_rule in zip(self.args[1::2], self.args[2::2]):
            filter_results_list.append((filter_range, filter_rule.match(text)))

        target_results = target_rule.match(text)
        ret_results = Results()
        for target_result in target_results:
            # 逐个 filter 规则过滤
            for filter_range, filter_results in filter_results_list:
                # 某条规则命中, 过滤, 其他规则可以不用考虑了
                if filter_range.filter(target_result, filter_results):
                    break
            else:  # 没有被过滤则加进去
                ret_results.add(target_result)

        return ret_results
