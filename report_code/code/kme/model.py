# -*- coding: utf-8 -*-
"""
模型对象
"""
from __future__ import unicode_literals

import os
from warnings import warn

import six

from .concept import Concept, ConceptManager
from .syntax import SyntaxManager
from .text.text import Text

if six.PY2:
    from codecs import open


class Model(object):
    """
    模型, 作为一个整体进行操作, 可以理解为所有规则的入口对象.
    """

    @classmethod
    def train(cls, rule_dir_path, config):
        """
        处理规则文件夹, 生成模型对象

        :param rule_dir_path: 规则目录路径
        :param config: 存储配置信息的对象
        :return: 返回模型对象
        """
        if not os.path.exists(rule_dir_path):
            raise ValueError('rule_dir_path does not exist', rule_dir_path)
        if not os.path.isdir(rule_dir_path):
            raise ValueError('rule_dir_path is not a dir', rule_dir_path)

        # 目录下的所有文件
        concept_mgr = ConceptManager(config)
        syntax_mgr = SyntaxManager(concept_mgr, config)
        for root, dirs, files in os.walk(rule_dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                concept_name, suffix = file_name.rsplit('.', 1)
                if suffix != 'def':  # 只接受 XXXX.def 这样的命名方式
                    continue

                with open(file_path, encoding='utf-8') as f:
                    try:
                        text = f.read()
                        rules, concept_filters = syntax_mgr.parse(text)
                        concept = Concept(config, concept_name, rules, concept_filters)
                        concept_mgr.add(concept)
                    except Exception as e:
                        warn(file_path)
                        raise e

        return cls(concept_mgr, config)

    def __init__(self, concept_mgr, config):
        self.concept_mgr = concept_mgr
        self.config = config

    def match(self, text, filter_by_concept_name=lambda x: False):
        """
        匹配, 模型会对每个 concept 进行一次匹配

        :param text: 输入的文档字符串
        :param filter_by_concept_name: 用于过滤部分不需要运行的 concept
                                       实际上是一个函数, 输入为 concept_name,
                                       输出为是否要运行, 默认为所有都运行
                                       (即: 所有都返回 False)
        :return: 返回 {concept_name: Results} 的 dict
        """
        if isinstance(text, six.text_type):
            text = Text.new(text, self.config)
        else:
            raise ValueError('invalid text type')

        concept_results = self.concept_mgr.match(text, filter_by_concept_name)
        return concept_results
