# -*- coding: utf-8 -*-
"""
概念对象
"""
from __future__ import unicode_literals

from ..result import Results


class Concept(object):
    """
    概念对象是规则的集合, 可以一定程度标定客观物理世界的一些通用规范. 例如, 我们规则中会大量使用到 "手机" 这个概念,
    我们可以建立一个 "Phone" 的概念, 对应给它赋予一些规则来表征.

        concept_name = Phone
        rules = [
            $kw("mobilephone"),
            $kw("phone"),
            $seq("mobile", "phone"),
            $ord(@d5, "my", "phone"),
            ...
        ]
    """

    def __init__(self, config, name, rules_or_filters, concept_filters=[]):
        """
        初始化一个 Concept 对象

        :param config: 包含配置信息的对象
        :param name: 概念名称
        :param rules_or_filters: 概念的匹配规则或规则过滤器, 规则与规则之间是 "逻辑或" 的操作, 即所有规则命中结果的集合
        :param concept_filters: 概念过滤器, 用在所有的结果上进行过滤, 默认不存在
        """
        self.config = config
        self.name = name
        if len(rules_or_filters) == 0:
            raise ValueError('concept has one rule or filter at least',name)
        self.rules_or_filters = rules_or_filters
        self.concept_filters = concept_filters

    def match(self, text):
        """
        匹配操作, 该概念能匹配到什么结果

        :param text: 待匹配的文本 Text 对象
        :return: 返回匹配到的结果, 会使用 global_rules 进行过滤
        """
        results = Results()
        for rule_or_filter in self.rules_or_filters:
            results.add(rule_or_filter.match(text))

        for concept_filter in self.concept_filters:
            results = concept_filter.filter(text, results)

        # 修改每个 Result 的 bias
        if self.config.get('force_concept_size_one', False):
            for result in results:
                # 相同的段落/句子, 则 bias 设置为end_index.i_word - beg_index.i_word - 1
                if result.beg_index.i_para == result.end_index.i_para \
                        and result.beg_index.i_sent == result.end_index.i_sent:
                    result.bias = result.end_index.i_word - result.beg_index.i_word
                else:  # 不在一个段落/句子中, 则直接设置为总长度 - 1, 保证其长度直接为 1
                    result.bias = result.end_index.i_word - 1

        return results
