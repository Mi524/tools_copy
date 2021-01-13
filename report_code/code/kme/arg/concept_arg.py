# -*- coding: utf-8 -*-
"""
概念参数
"""
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class ConceptArg(object):
    """
    概念参数, 其必须符合如下几个规范:

        * 名称唯一标识一个概念 (全项目)
        * 名称只能出现:
            1. 阿拉伯数字
            2. 英文字母 (大小写敏感)
            3. 下划线

    由于在编写过程中的先后顺序可能会导致概念的引用比初始化早的情况发生,
    所以初始化 ConceptArg 时不会直接获取 Concept 对象, 而是在 match 的时候动态获取.
    """

    def __init__(self, config, name, beg_index, end_index, concept_mgr):
        """
        初始化一个概念参数

        :param config: 存储配置信息的对象
        :param name: 概念名称, 全局唯一
        :param beg_index: 当前 arg 在语法文本中的起始下标 (闭区间)
        :param end_index: 当前 arg 在语法文本中的结束下标 (开区间)
        :param concept_mgr: 用来存储管理 concept_name => Concept 的对象
        """
        self.config = config
        self.name = name
        self.beg_index = beg_index
        self.end_index = end_index
        self.concept_mgr = concept_mgr

    def __str__(self):
        return 'ConceptArg(name={}, beg_index={}, end_index={})'.format(
            self.name,
            self.beg_index,
            self.end_index,
        )

    def match(self, text):
        """
        匹配对象进行文本的规则匹配

        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象
        """
        # 不存在会报错, 这里我考虑如果做兼容性考量, 生成一个不起任何作用的 ConceptArg,
        # 势必会带来 "不好探查的错误", 因为从实际使用角度来说不存在无意义的空概念存在,
        # 只可能是拼写错误之类的错误导致, 所以报错可以让用户在测试阶段就发现问题.
        concept = self.concept_mgr.get(self.name)
        results = concept.match(text)
        return results
