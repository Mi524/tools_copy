# -*- coding: utf-8 -*-
"""
用来管理 Concept 的对象, 可以实现 concept_name => Concept 的映射
"""
from __future__ import unicode_literals

from .concept import Concept


class ConceptManager(dict):
    """
    概念管理器, 本质上是一个 dict, 可以用过 concept_name 得到 Concept 对象
    """

    def __init__(self, config):
        """
        初始化
        :param config: 包含配置信息的对象
        """
        self.config = config

    def get(self, concept_name):
        """
        通过 concept_name 获取对应的 Concept 对象

        :param concept_name: 概念名称, 唯一标志一个概念
        :return: 返回概念, 不存在则报错 KeyError
        """
        return self.__getitem__(concept_name)

    def add(self, concept):
        """
        添加一个概念

        :param concept: 待添加的概念
        """
        if not isinstance(concept, Concept):
            raise ValueError('concept must be Concept object', concept)

        self.__setitem__(concept.name, concept)

    def match(self, text, filter_by_concept_name=lambda x: False):
        """
        所有 concept 逐个 match

        :param text: Text 对象
        :param filter_by_concept_name: 用于过滤部分不需要运行的 concept
                                       实际上是一个函数, 输入为 concept_name,
                                       输出为是否要运行, 默认为所有都运行
                                       (即: 所有都返回 False)
        :return: 返回命中有结果 {concept_name: Results} dict
        """
        ret = {}
        for concept_name, concept in self.items():
            if not filter_by_concept_name(concept_name):
                results = concept.match(text)
                if len(results) > 0:
                    ret[concept_name] = results
        return ret
