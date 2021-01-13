# -*- coding: utf-8 -*-
"""
规则的基类
"""
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class BaseRule(object):
    """
    构造函数和 __str__ 是一样的, 没必要多次实现.
    """

    # 默认支持的参数类型名称
    default_supported_arg_names = ('KeywordArg', 'SingleKeywordArg', 'ConceptArg', 'ArgRule', 'BagRule',
                                   'OrRule', 'OrdRule', 'SeqRule', 'RuleFilter')

    def __init__(self, config, beg_index, end_index, *args):
        """
        初始化一个规则对象

        :param config: 存储配置信息的对象
        :param beg_index: 当前规则在语法文本中的起始下标 (闭区间)
        :param end_index: 当前规则在语法文本中的结束下标 (开区间)
        :param args: 参数列表
        """
        self.config = config
        self.args = args
        self.beg_index = beg_index
        self.end_index = end_index
        self.validate()

    def validate(self):
        """
        合法性检验

        :return: 检验不合法直接抛出异常
        """
        pass

    def __str__(self):
        return '{}(args=[{}], beg_index={}, end_index={})'.format(
            self.__class__.__name__,
            ', '.join([six.text_type(x) for x in self.args]),
            self.beg_index,
            self.end_index,
        )
