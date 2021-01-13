# -*- coding: utf-8 -*-
"""
袋规则
"""
from __future__ import unicode_literals

import copy

import six

from .base_rule import BaseRule
from ..result import Result, Results


class BagRule(BaseRule):
    """
    袋规则, 包括3个特性:

        1. 无序. 是指规则中的参数前后顺序不敏感, 就像个袋子一样
        2. 不连续. 是指规则参数不需要紧密连续, 中间可以出现若干其他无关词条
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
            raise ValueError('BagRule needs TWO arguments at least')

        # 2. 第 1 个参数必须是规则范围
        if self.args[0].__class__.__name__ != 'RuleRangeArg':
            raise ValueError('The first argument of BagRule must be RuleRangeArg')

        # 3. 之后的参数类别限制
        for index, arg in enumerate(self.args[1:]):
            arg_name = arg.__class__.__name__
            if arg_name not in self.__class__.default_supported_arg_names:
                raise ValueError('BagRule only support argument of types ({})'.format(
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
                # 利用 bit_map 判断是否有重叠
                bit_map = [0] * len(tmp_results[0].word_list)
                # 重新生成一个 result
                min_beg_offset = 999999
                min_beg_index = None
                max_end_offset = -1
                max_end_index = None
                total_bias = 0
                for tmp_result in tmp_results:
                    # 有重叠
                    if sum(bit_map[tmp_result.beg_index.offset: tmp_result.end_index.offset + 1]) > 0:
                        return

                    # 累加 bias
                    total_bias += tmp_result.bias

                    # 没重叠添加当前结果覆盖的部分的部分
                    for i in six.moves.range(tmp_result.beg_index.offset, tmp_result.end_index.offset + 1):
                        bit_map[i] = 1

                    if tmp_result.beg_index.offset < min_beg_offset:
                        min_beg_offset = tmp_result.beg_index.offset
                        min_beg_index = tmp_result.beg_index
                    if tmp_result.end_index.offset > max_end_offset:
                        max_end_offset = tmp_result.end_index.offset
                        max_end_index = tmp_result.end_index

                result = Result(self.config, tmp_results[0].word_list, min_beg_index, max_end_index, total_bias)
                results.add(result)
            return

        for result in results_cache[index]:
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
