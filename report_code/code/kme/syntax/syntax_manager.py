# -*- coding: utf-8 -*-
"""
语法分析管理器, 所有语法分析的入口位置
"""
from __future__ import unicode_literals

from .comment_syntax import CommentSyntax
from .concept_filter_syntax import ConceptFilterSyntax
from .concept_syntax import ConceptSyntax
from .filter_range_syntax import FilterRangeSyntax
from .keyword_syntax import KeywordSyntax
from .rule_filter_syntax import RuleFilterSyntax
from .rule_range_syntax import RuleRangeSyntax
from .rule_syntax import RuleSyntax


class SyntaxManager(object):
    """
    语法分析管理器, 语法分析管理器只会处理2种类别的资源:

        * 规则, 以 $ 起始的资源
        * 注释, 以 # 起始的资源

    输入的规则代码支持多行输入, 如果存在语法错误会直接报错
    """

    def __init__(self, concept_mgr, config):
        """
        初始化
        :param concept_mgr: 用来存储管理 concept_name => Concept 的对象
        :param config: 存储配置信息的对象
        """
        self.concept_mgr = concept_mgr
        self.config = config

    @staticmethod
    def ignore_space(text, index):
        """
        忽略 "空" 字符, 空字符为:

            * 空格
            * 制表符
            * 换行符

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 返回不是 "空" 字符的索引
        """
        while index < len(text):
            if text[index] in '\t\n\r ':
                index += 1
                continue
            break
        return index

    def parse_args(self, text, index):
        """
        处理一条规则的, 参数列表. 如果规则中包含规则则会进入迭代. 返回的是当前规则的 args 和结束位置

        :param text: 全量文本
        :param index: 待处理得参数的起始下标
        :return: 返回 4 个对象, 分别为:
            * 范围参数, 每个规则仅一条,
            * 匹配参数, 用于匹配结果 (按顺序)
            * 限制参数, 用户最后结果的限制
            * 结束的位置 (方便后续匹配使用)
        """
        # 参数列表
        args = []
        while index < len(text):
            # 先干掉前面的 "空字符"
            index = self.ignore_space(text, index)
            # 匹配到 ), 表示当前规则结束
            if text[index] == ')':  # 规则结束
                # 返回参数列表和结束的 index
                return args, index + 1
            elif text[index] == ',':  # 还有其他参数, 继续
                index += 1
                continue

            # 逐个判断当前字符开始是那种类别
            for syntax in (
                    KeywordSyntax,  # 关键词
                    RuleSyntax,  # 规则
                    ConceptSyntax,  # 概念
                    RuleRangeSyntax,  # 适用于规则的范围
                    FilterRangeSyntax,  # 适用于过滤器的范围
                    RuleFilterSyntax,  # 规则过滤器
                    ConceptFilterSyntax,  # 概念过滤器
                    CommentSyntax,  # 注释
            ):
                match = syntax.match(self.config, text, index, concept_mgr=self.concept_mgr)
                if match:  # 找到了当前字符开始属于哪个类别
                    # 是否是注释, 注释则直接跳过
                    if syntax is CommentSyntax:
                        index = match.end_index
                    elif (syntax is KeywordSyntax
                          or syntax is ConceptSyntax
                          or syntax is RuleRangeSyntax
                          or syntax is FilterRangeSyntax):
                        args.append(match)
                        index = match.end_index
                    elif (syntax is RuleSyntax
                          or syntax is RuleFilterSyntax
                          or syntax is ConceptFilterSyntax):
                        # 匹配先会匹配到 header
                        arg_index = match.arg_index
                        curr_args, end_index = self.parse_args(text, arg_index)
                        rule_or_filter = match.assemble(curr_args, end_index)
                        args.append(rule_or_filter)
                        index = rule_or_filter.end_index
                    else:  # 理论上不会出现, 出现就是代码有 BUG
                        raise ValueError('invalid arg', text[index:])
                    break
            else:  # 遍历完所有的 syntax, 没有匹配的
                raise ValueError('unknown arg', text[index:])
        else:
            raise ValueError('incomplete args', text[index:])

    def parse(self, text):
        """
        语法处理输入文本, 请务必保证输入的文本是完整的若干规则/注释的集合

        :param text: 输入的规则代码
        :return: 返回规则或规则过滤器的列表, 概念过滤器列表
        """
        index = 0
        rules_or_filters = []
        concept_filters = []
        # 干掉前后的空字符
        text = text.strip()
        while index < len(text):
            # 先把 "空字符" 去掉
            index = self.ignore_space(text, index)

            # 注释
            comment = CommentSyntax.match(self.config, text, index)
            if comment:  # 是注释, 忽略
                index = comment.end_index
                continue

            # 规则
            match = RuleSyntax.match(self.config, text, index)
            if match:  # 是规则
                index = match.arg_index
                args, index = self.parse_args(text, index)
                rule = match.assemble(args, index)
                rules_or_filters.append(rule)
                continue

            # 规则过滤器
            match = RuleFilterSyntax.match(self.config, text, index)
            if match:  # 是规则过滤器
                index = match.arg_index
                args, index = self.parse_args(text, index)
                rule_filter = match.assemble(args, index)
                rules_or_filters.append(rule_filter)
                continue

            # 概念过滤器
            match = ConceptFilterSyntax.match(self.config, text, index)
            if match:  # 是概念过滤器
                index = match.arg_index
                args, index = self.parse_args(text, index)
                concept_filter = match.assemble(args, index)
                concept_filters.append(concept_filter)
                continue

            # 其余报错
            raise ValueError('invalid rule', text[index:])

        return rules_or_filters, concept_filters
