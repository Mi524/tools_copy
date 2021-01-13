# -*- coding: utf-8 -*-
"""
过滤范围参数
"""
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class FilterRangeArg(object):

    def __init__(self, config, forward_unit, forward_n, is_overlap, backward_unit, backward_n, beg_index, end_index):
        """
        初始化一个 FilterRangeArg 对象

        :param config: 存储配置信息的对象
        :param forward_unit: 前向范围单位 [dwspt]
        :param forward_n: 前向范围数值, 仅支持正整数, 如果为 0 表示不进行前向范围过滤
        :param is_overlap: 重叠过滤标志位, True / False
        :param backward_unit: 后向范围单位 [dwspt]
        :param backward_n: 后向范围数值, 仅支持正整数, 如果为 0 表示不进行前向范围过滤
        :param beg_index: 当前 arg 在语法文本中的起始下标 (闭区间)
        :param end_index: 当前 arg 在语法文本中的结束下标 (开区间)
        """
        self.config = config
        self.forward_unit = forward_unit
        self.forward_n = int(forward_n)
        self.is_overlap = bool(is_overlap)
        self.backward_unit = backward_unit
        self.backward_n = int(backward_n)
        self.beg_index = beg_index
        self.end_index = end_index
        self.unit_map = {
            'd': self.filter_d,
            'w': self.filter_w,
            's': self.filter_s,
            'p': self.filter_p,
            't': self.filter_t,
        }

    def __str__(self):
        return ('FilterRangeArg(forward_unit={}, forward_n={}, is_overlap={}, '
                'backward_unit={}, backward_n={}, beg_index={}, end_index={})').format(
            self.forward_unit,
            self.forward_n,
            self.is_overlap,
            self.backward_unit,
            self.backward_n,
            self.beg_index,
            self.end_index,
        )

    def filter_d(self, target_result, filter_results, n, dir):
        """
        单位为 d 的过滤判断

        :param filter_results: 进行过滤的结果
        :param target_result: 待过滤的目标结果
        :param n: 单位对应的 n
        :param dir: 前向或后向, 仅支持 forward / backward
        :return: 返回是否过滤
        """
        for fr in filter_results:
            # 不与自己进行比较
            if fr == target_result:
                continue

            if dir == 'forward':
                if fr.end_index.i_para == target_result.beg_index.i_para \
                        and fr.end_index.i_sent == target_result.beg_index.i_sent \
                        and target_result.beg_index.i_word > fr.end_index.i_word >= target_result.beg_index.i_word - n:
                    return True
            elif dir == 'backward':
                if fr.beg_index.i_para == target_result.end_index.i_para \
                        and fr.beg_index.i_sent == target_result.end_index.i_sent \
                        and target_result.end_index.i_word < fr.beg_index.i_word <= target_result.end_index.i_word + n:
                    return True
            else:
                raise ValueError('invalid dir parameter')

        return False

    def filter_w(self, target_result, filter_results, n, dir):
        """
        单位为 w 的过滤判断

        :param filter_results: 进行过滤的结果
        :param target_result: 待过滤的目标结果
        :param n: 单位对应的 n
        :param dir: 前向或后向, 仅支持 forward / backward
        :return: 返回是否过滤
        """
        for fr in filter_results:
            # 不与自己进行比较
            if fr == target_result:
                continue

            if dir == 'forward':
                if fr.end_index.i_para == target_result.beg_index.i_para \
                        and target_result.beg_index.offset > fr.end_index.offset >= target_result.beg_index.offset - n:
                    return True
            elif dir == 'backward':
                if fr.beg_index.i_para == target_result.end_index.i_para \
                        and target_result.end_index.offset < fr.beg_index.offset <= target_result.end_index.offset + n:
                    return True
            else:
                raise ValueError('invalid dir parameter')

        return False

    def filter_s(self, target_result, filter_results, n, dir):
        """
        单位为 s 的过滤判断

        :param filter_results: 进行过滤的结果
        :param target_result: 待过滤的目标结果
        :param n: 单位对应的 n
        :param dir: 前向或后向, 仅支持 forward / backward
        :return: 返回是否过滤
        """
        for fr in filter_results:
            # 不与自己进行比较
            if fr == target_result:
                continue

            if dir == 'forward':
                if fr.end_index.i_para == target_result.beg_index.i_para \
                        and target_result.beg_index.i_sent > fr.end_index.i_sent >= target_result.beg_index.i_sent - n:
                    return True
            elif dir == 'backward':
                if fr.beg_index.i_para == target_result.end_index.i_para \
                        and target_result.end_index.i_sent < fr.beg_index.i_sent <= target_result.end_index.i_sent + n:
                    return True
            else:
                raise ValueError('invalid dir parameter')

        return False

    def filter_p(self, target_result, filter_results, n, dir):
        """
        单位为 p 的过滤判断

        :param filter_results: 进行过滤的结果
        :param target_result: 待过滤的目标结果
        :param n: 单位对应的 n
        :param dir: 前向或后向, 仅支持 forward / backward
        :return: 返回是否过滤
        """
        for fr in filter_results:
            # 不与自己进行比较
            if fr == target_result:
                continue

            if dir == 'forward':
                if target_result.beg_index.i_para > fr.end_index.i_para >= target_result.beg_index.i_para - n:
                    return True
            elif dir == 'backward':
                if target_result.end_index.i_para < fr.beg_index.i_para <= target_result.end_index.i_para + n:
                    return True
            else:
                raise ValueError('invalid dir parameter')

        return False

    def filter_t(self, target_result, filter_results, n, dir):
        """
        单位为 t 的过滤判断

        :param filter_results: 进行过滤的结果
        :param target_result: 待过滤的目标结果
        :param n: 单位对应的 n
        :param dir: 前向或后向, 仅支持 forward / backward
        :return: 返回是否过滤
        """
        for fr in filter_results:
            # 不与自己进行比较
            if fr == target_result:
                continue

            if dir == 'forward':
                if fr.end_index.offset < target_result.beg_index.offset:
                    return True
            elif dir == 'backward':
                if fr.beg_index.offset > target_result.end_index.offset:
                    return True
            else:
                raise ValueError('invalid dir parameter')

        return False

    def filter_overlap(self, target_result, filter_results):
        """
        重叠过滤的判断

        :param filter_results: 进行过滤的结果
        :param target_result: 待过滤的目标结果
        :return: 返回是否过滤
        """
        for fr in filter_results:
            if target_result.overlap(fr):
                return True
        return False

    def filter(self, target_result, filter_results):
        """
        对某个目标规则的结果进行过滤

        :param target_result: 目标规则的结果
        :param filter_results: 进行过滤的过滤规则匹配到的结果
        :return: 返回是否要将 target_result 过滤
        """
        if self.forward_n > 0:
            func = self.unit_map[self.forward_unit]
            if func(target_result, filter_results, self.forward_n, 'forward'):
                return True
        if self.backward_n > 0:
            func = self.unit_map[self.backward_unit]
            if func(target_result, filter_results, self.backward_n, 'backward'):
                return True
        if self.is_overlap:
            if self.filter_overlap(target_result, filter_results):
                return True

        return False
