# -*- coding: utf-8 -*-
"""
范围参数, 用来作为规则的范围限制条件
"""
from __future__ import unicode_literals

import six

from ..result import Results


@six.python_2_unicode_compatible
class RuleRangeArg(object):
    """
    范围参数, 其必须符合如下规范:

        * 范围的标定单位只能从 d|w|s|p|t 中选择一个
        * 范围的标定标量只能是 大于 0 的正整数

    其可选的范围如下:

    | *单位* | *注释*              | *示例*                            |
    | ----- | ------------------- | --------------------------------- |
    | d     | 不跨句子的范围        | 若参数为1，则@d即可，若n为6则为：@d6 |
    | w     | 跨句子的范围, 不跨段落 | 参数若为1，则@w即可，若n为8则为：@w8 |
    | s     | 句子                 | 参数若为1，则@s即可，若n为7则为：@s7 |
    | p     | 段落                 | 参数若为1，则@p即可，若n为5则为：@p5 |
    | t     | 整文                 | 没有参数，表示全文，@t              |
    """

    def __init__(self, config, unit, n, beg_index, end_index):
        """
        初始化 range 对象

        :param config: 存储配置信息的对象
        :param unit: 范围的标定单位
        :param n: 范围标定的标量
        :param beg_index: 当前 arg 在语法文本中的起始下标 (闭区间)
        :param end_index: 当前 arg 在语法文本中的结束下标 (开区间)
        """
        self.config = config
        self.unit = unit
        self.n = int(n)
        if self.n <= 0:
            raise ValueError('invalid parameter n', n)
        self.beg_index = beg_index
        self.end_index = end_index

    def __str__(self):
        return 'RuleRangeArg(unit={}, n={}, beg_index={}, end_index={})'.format(
            self.unit,
            self.n,
            self.beg_index,
            self.end_index
        )

    def filter(self, results):
        """
        对已经匹配的对象进行范围过滤, 滤除不合规格的

        :param results: 已经匹配的结果
        :return: 返回滤除后的合规范结果
        """

        def filter_d(result):
            """
            不跨句子的词/字级别范围判断
            """
            if result.end_index.i_para == result.beg_index.i_para \
                    and result.end_index.i_sent == result.beg_index.i_sent:
                # 字/词的判断
                if self.config.get('force_concept_size_one', False):  # concept 强制为长度 1
                    return result.end_index.i_word - result.beg_index.i_word + 1 - result.bias <= self.n
                else:  # concept 不强制为长度 1
                    return result.end_index.i_word - result.beg_index.i_word + 1 <= self.n
            else:  # 段落/句子已经不满足
                return False

        def filter_w(result):
            """
            跨句子的词/字级别范围判断
            """
            if result.end_index.i_para == result.beg_index.i_para:
                if self.config.get('force_concept_size_one', False):  # concept 强制为长度 1
                    return result.end_index.offset - result.beg_index.offset + 1 - result.bias <= self.n
                else:  # concept 不强制为长度 1
                    return result.end_index.offset - result.beg_index.offset + 1 <= self.n
            else:
                return False

        def filter_s(result):
            """
            不跨段落的句子级别范围判断
            """
            return result.end_index.i_para == result.beg_index.i_para \
                   and result.end_index.i_sent - result.beg_index.i_sent + 1 <= self.n

        def filter_p(result):
            """
            段落级别的范围判断
            """
            return result.end_index.i_para - result.beg_index.i_para + 1 <= self.n

        if self.unit == 't':  # 整个文本的不用过滤
            return results

        # 依据 unit 来选定过滤函数, 过滤函数为 "留下的条件"
        if self.unit == 'd':  # 不跨越句子的词条数目
            filter_func = filter_d
        elif self.unit == 'w':  # 跨越句子的词条数目
            filter_func = filter_w
        elif self.unit == 's':  # 句子数目
            filter_func = filter_s
        elif self.unit == 'p':  # 段落数目
            filter_func = filter_p
        else:
            raise ValueError('invalid unit', self.unit)

        ret_results = Results()
        for result in results:
            if filter_func(result):
                ret_results.add(result)

        return ret_results


# 默认 @t 参数
t_range_arg = RuleRangeArg(None, 't', 1, 0, 0)

# 默认 @s 参数
s_range_arg = RuleRangeArg(None, 's', 1, 0, 0)
