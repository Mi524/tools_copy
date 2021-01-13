# -*- coding: utf-8 -*-
"""
用于过滤器中的范围标定
"""
from __future__ import unicode_literals

import re

from ..arg import FilterRangeArg


class FilterRangeSyntax(object):
    """
    用于过滤器中的范围标定, 其格式为:

        @[前向范围, 重叠标志位, 后向范围]

    其中, 前向/后向范围均支持 "单位 + 数值" 的方案, 其类似于 RuleRangeSyntax.
    如果不作过滤则标记为 0 即可, 重叠标志位仅支持 1 / 0, 分别表示过滤和不过滤

    | *单位* | *注释*       | *示例*                            |
    | ----- | ------------ | --------------------------------- |
    | d     | 不跨句子的范围 | 若参数为1，则 d 即可，若n为6则为：d6 |
    | w     | 跨句子的范围   | 参数若为1，则 w 即可，若n为8则为：w8 |
    | s     | 句子          | 参数若为1，则 s 即可，若n为7则为：s7 |
    | p     | 段落          | 参数若为1，则 p 即可，若n为5则为：p5 |
    | t     | 整文          | 没有参数，表示全文，t              |
    """
    re_match = re.compile(r'@\[{sp}({ut}\d*|0){sp},{sp}(\d+){sp},{sp}({ut}\d*|0){sp}\]{sp},'.format(
        ut=r'[dwspt]',  # 单位
        sp=r'[ \t\n\r]*',  # 空格
    ))

    @classmethod
    def match(cls, config, text, index, *args, **kwargs):
        """
        依据 text[index] 判断是否是范围

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回范围对象, 不成功返回 None
        """
        if text.startswith('@[', index):
            m = cls.re_match.match(text, index)
            if m:
                beg_index, end_index = m.span(0)
                # 不要 , 带来的 index
                end_index -= 1
                # 前向范围
                forward = m.group(1)
                if forward == '0':  # 如果为 0 表示不作过滤
                    forward_unit = None
                    forward_n = 0
                else:  # 过滤
                    forward_unit = forward[0]
                    if forward[1:]:  # 单位 + 数值
                        forward_n = int(forward[1:])
                    else:  # 纯单位
                        forward_n = 1

                # 重叠标志位
                is_overlap = bool(int(m.group(2)))

                # 后向范围
                backward = m.group(3)
                if backward == '0':  # 如果为 0 表示不作过滤
                    backward_unit = None
                    backward_n = 0
                else:  # 过滤
                    backward_unit = backward[0]
                    if backward[1:]:  # 单位 + 数值
                        backward_n = int(backward[1:])
                    else:  # 纯单位
                        backward_n = 1

                return FilterRangeArg(config, forward_unit, forward_n, is_overlap,
                                      backward_unit, backward_n, beg_index, end_index)
            else:
                raise ValueError('invalid filter_range_arg', text[index:])
