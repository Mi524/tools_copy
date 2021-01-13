# -*- coding: utf-8 -*-
"""
有序连续规则
"""
from __future__ import unicode_literals

import copy

from .base_rule import BaseRule
from ..result import Result, Results


class SeqRule(BaseRule):
    """
    有序连续规则, 包括3个特性:

        1. 有序. 是指规则中的参数前后顺序是敏感的
        2. 连续. 是指规则参数需要紧密连续, 中间不可以出现若干其他无关词条
        3. 不重叠. 匹配的元素和元素之间不能出现重叠
    """

    def validate(self):
        """
        参数的合法性检验, 不合法抛出异常.

        1. 参数至少要 2 个
        2. 第 1 个参数必须是规则范围 (RuleRangeArg)
        3. 第 2 个及以后的参数可以是:
            1) 关键词 (KeywordArg)
            2) 概念 (ConceptArg)
            3) 规则 (ArgRule, BagRule, OrRule, OrdRule, SeqRule)
            4) 规则过滤器 (RuleFilter)
        """
        # 1. 参数至少要 2 个
        if len(self.args) < 2:
            raise ValueError('SeqRule needs TWO arguments at least')

        # 2. 第 1 个参数必须是规则范围
        if self.args[0].__class__.__name__ != 'RuleRangeArg':
            raise ValueError('The first argument of SeqRule must be RuleRangeArg')

        # 3. 之后的参数类别限制
        for index, arg in enumerate(self.args[1:]):
            arg_name = arg.__class__.__name__
            if arg_name not in self.__class__.default_supported_arg_names:
                raise ValueError('SeqRule only support argument of types ({})'.format(
                    ', '.join(self.__class__.default_supported_arg_names)
                ), index + 1, arg_name)

    def recur_compose_result(self, results_cache, tmp_results, index, results):
        """
        递归来组合结果. 依据输入的每个 arg 对应的 Results, 通过 arg 的前后顺序进行筛选.

        :param results_cache: 逐个 arg 对应的 Results 对象
        :param tmp_results: 当前组合的已完成结果, 记录的是每个 arg 对应的一种 Result 情况
        :param index: 当前计算的 results_cache 的索引号
        :param results: 最终存放组合完毕的 Result (输出)
        """
        if index == len(results_cache):  # 所有都运行完成
            if len(tmp_results) == len(results_cache):  # 匹配的部分
                # 所有 Result 的 bias 求和
                total_bias = sum([result.bias for result in tmp_results])
                # 重新生成一个 result
                result = Result(
                    self.config,
                    tmp_results[0].word_list,
                    tmp_results[0].beg_index,
                    tmp_results[-1].end_index,
                    total_bias
                )
                results.add(result)
            return

        if index == 0 and not tmp_results:  # 还没有数据
            for result in results_cache[index]:  # 第一列
                cur_results = copy.copy(tmp_results)
                cur_results.append(result)
                self.recur_compose_result(results_cache, cur_results, index + 1, results)
        else:  # 非第一列 results
            last_result = tmp_results[-1]
            for result in results_cache[index]:  # 第 index 列
                if last_result.end_index.offset + 1 == result.beg_index.offset:
                    cur_results = copy.copy(tmp_results)
                    cur_results.append(result)
                    self.recur_compose_result(results_cache, cur_results, index + 1, results)

    def match(self, text):
        """
        匹配对象进行文本的规则匹配

        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回 None
        """
        rule_range = self.args[0]
        match_args = self.args[1:]
        # 如果没有匹配到就返回一个空的 Results
        results = Results()
        # 用来存放每个 arg 的匹配 Results
        results_cache = []
        for arg in match_args:
            arg_results = arg.match(text)
            if len(arg_results) == 0:
                return results
            else:
                results_cache.append(arg_results)

        # 递归拼接结果
        self.recur_compose_result(results_cache, [], 0, results)

        # 使用范围参数过滤
        results = rule_range.filter(results)

        return results
