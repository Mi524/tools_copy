# -*- coding: utf-8 -*-
"""
关键词的语法分析
"""
from __future__ import unicode_literals

import re

from ..arg import KeywordArg


class KeywordSyntax(object):
    """
    关键词使用 " 囊括来标定, 对于要表达的双引号, 使用 \ 进行转义, 例如:

        * "ABC", 表示关键词 ABC
        * "A\"BC", 表示关键词 A"BC

    默认情况下, 关键词会进行 lemmatize (英文环境), 如果匹配时希望匹配原始词条, 可在关键词的前引号前附加 r, 例如:

        * "loves", 会被 lemmatize 后匹配 love
        * r"loves", 会忽略 lemmatize, 仅匹配 loves

    关键词中不许出现:

        * 空格
        * 制表符, 即 \t
        * 换行, 即 \n
        * 无转义的双引号, "ab"c" 这种会报错
    """

    re_match = re.compile(r'"(([^"\t\n ]|(?<=\\)")+)(?<!\\)"[\n\t ]*[),]')

    @classmethod
    def match(cls, config, text, index, *args, **kwargs):
        """
        关键词的语法匹配, 依据 text[index] 判断是否是关键词. 如若匹配上返回关键词对象, 可用来匹配文本.

        :param config: 存储配置信息的对象
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回关键词语法对象, 不成功返回 None
        """
        # 会先匹配 ", 以提高效率
        if text[index] == 'r':  # 可能是 raw
            index += 1
        if text[index] == '"':  # 双引号
            m = cls.re_match.match(text, index)
            if m:
                word = m.group(1)
                beg_index, end_index = m.span(0)
                # 不要 ), 带来的 index
                end_index -= 1
                # 是否是原始词条 (没有 lemmatize)
                is_raw = False
                if index > 0 and text[index - 1] == 'r':
                    is_raw = True

                if is_raw:  # 如果有 r, 就从 r 开始计数
                    beg_index -= 1

                return KeywordArg(config, is_raw, word, beg_index, end_index)
            else:  # 以引号开头，但是匹配不上
                raise ValueError('invalid keyword', text[index:])
