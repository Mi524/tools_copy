# -*- coding: utf-8 -*-
"""
范围限制器的语法分析
"""
from __future__ import unicode_literals

import re

from ..arg import RuleRangeArg


class RuleRangeSyntax(object):
    """
    范围限制器使用 @ 来标定, 具体的范围指令包括:

    | *单位* | *注释*       | *示例*                            |
    | ----- | ------------ | --------------------------------- |
    | d     | 不跨句子的范围 | 若参数为1，则@d即可，若n为6则为：@d6 |
    | w     | 跨句子的范围   | 参数若为1，则@w即可，若n为8则为：@w8 |
    | s     | 句子          | 参数若为1，则@s即可，若n为7则为：@s7 |
    | p     | 段落          | 参数若为1，则@p即可，若n为5则为：@p5 |
    | t     | 整文          | 没有参数，表示全文，@t              |
    """

    re_match = re.compile(r'@([dwspt])(\d*)[\t\n ]*,')

    @classmethod
    def match(cls, config, text, index, *args, **kwargs):
        """
        依据 text[index] 判断是否是范围

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回范围对象, 不成功返回 None
        """
        if text[index] == '@' and text[index + 1] != '[':
            m = cls.re_match.match(text, index)
            if m:
                unit, n = m.groups()
                n = 1 if n == '' else int(n)
                beg_index, end_index = m.span(0)
                # 不要 , 对应的 index
                end_index -= 1
                return RuleRangeArg(config, unit, n, beg_index, end_index)
            else:
                raise ValueError('invalid range syntax', text[index:])
