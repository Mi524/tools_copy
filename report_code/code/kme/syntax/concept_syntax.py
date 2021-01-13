# -*- coding: utf-8 -*-
"""
概念的语法分析
"""
from __future__ import unicode_literals

import re

from ..arg import ConceptArg


class ConceptSyntax(object):
    """
    概念使用 _ 下划线起始来标定, 概念名称只能使用:

        1. 阿拉伯数字
        2. 英文字母 (大小写敏感)
        3. 下划线
        4. 横线

    例如:

        * _MobilePhone
        * _mobile_phone
        * _MOBILE_PHONE
    """

    re_match = re.compile(r'_([\w-]+)[\n\t ]*[),]')

    @classmethod
    def match(cls, config, text, index, concept_mgr, *args, **kwargs):
        """
        依据 text[index] 判断是否是概念

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :param concept_mgr: 用来存储管理 concept_name => Concept 的对象
        :return: 匹配成功返回概念对象, 不成功返回 None
        """
        if text[index] == '_':
            m = cls.re_match.match(text, index)
            if m:
                concept_name = m.group(1)
                beg_index, end_index = m.span(0)
                # 不要 ), 带来的 index
                end_index -= 1
                return ConceptArg(config, concept_name, beg_index, end_index, concept_mgr)
            else:
                raise ValueError('invalid concept', text[index:])
