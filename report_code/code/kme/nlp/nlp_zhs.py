# -*- coding: utf-8 -*-
"""
用于处理简体中文相关的自然语言工具
"""
from __future__ import unicode_literals

import re

import jieba
import jieba.posseg as pseg


class NlpZhs(object):
    """
    处理简体中文的 NLP 工具集
    """

    __re_sent = re.compile(u'[!。！…]')

    @classmethod
    def pos_tag(cls, words):
        """
        因为中文和英文不具有通用性, 所以词性上无法直接一套解决所有问题.
        此处的词性结构使用 jieba 的词性结构

        :param words:
        :return: 返回词和词性的列表.
        * Ag: 形语素. 形容词性语素. 形容词代码为 a，语素代码 g 前面置以 A
        * a: 形容词. 取英语形容词 adjective 的第 1 个字母
        * ad: 副形词. 直接作状语的形容词。形容词代码 a和副词代码d并在一起。
        * an: 名形词. 具有名词功能的形容词。形容词代码 a和名词代码n并在一起。
        * b: 区别词. 取汉字“别”的声母。
        * c: 连词. 取英语连词 conjunction的第1个字母。
        * dg: 副语素. 副词性语素。副词代码为 d，语素代码ｇ前面置以D。
        * d: 副词. 取 adverb的第2个字母，因其第1个字母已用于形容词。
        * e: 叹词. 取英语叹词 exclamation的第1个字母。
        * f: 方位词. 取汉字“方”
        * g: 语素. 绝大多数语素都能作为合成词的“词根”，取汉字“根”的声母。
        * h: 前接成分. 取英语 head的第1个字母。
        * i: 成语. 取英语成语 idiom的第1个字母。
        * j: 简称略语. 取汉字“简”的声母。
        * k: 后接成分.
        * l: 习用语. 习用语尚未成为成语，有点“临时性”，取“临”的声母。
        * m: 数词. 取英语 numeral的第3个字母，n，u已有他用。
        * Ng: 名语素. 名词性语素。名词代码为 n，语素代码ｇ前面置以N。
        * n: 名词. 取英语名词 noun的第1个字母。
        * nr: 人名. 名词代码 n和“人(ren)”的声母并在一起。
        * ns: 地名. 名词代码 n和处所词代码s并在一起。
        * nt: 机构团体. “团”的声母为 t，名词代码n和t并在一起。
        * nz: 其他专名. “专”的声母的第 1个字母为z，名词代码n和z并在一起。
        * o: 拟声词. 取英语拟声词 onomatopoeia的第1个字母。
        * p: 介词. 取英语介词 prepositional的第1个字母。
        * q: 量词. 取英语 quantity的第1个字母。
        * r: 代词. 取英语代词 pronoun的第2个字母,因p已用于介词。
        * s: 处所词. 取英语 space的第1个字母。
        * tg: 时语素. 时间词性语素。时间词代码为 t,在语素的代码g前面置以T。
        * t: 时间词. 取英语 time的第1个字母。
        * u: 助词. 取英语助词 auxiliary
        * vg: 动语素. 动词性语素。动词代码为 v。在语素的代码g前面置以V。
        * v: 动词. 取英语动词 verb的第一个字母。
        * vd: 副动词. 直接作状语的动词。动词和副词的代码并在一起。
        * vn: 名动词. 指具有名词功能的动词。动词和名词的代码并在一起。
        * w: 标点符号.
        * x: 非语素字. 非语素字只是一个符号，字母 x通常用于代表未知数、符号。
        * y: 语气词. 取汉字“语”的声母。
        * z: 状态词. 取汉字“状”的声母的前一个字母。
        * un: 未知词. 不可识别词及用户自定义词组。取英文Unkonwn首两个字母。
        * mg: 数量词语素
        * zg: 状态词语素
        * rr: 人称代词
        * ul: 连接习惯用语的连接词. 了, 喽
        * df: 不要
        * nrfg: 人名
        * uv: 接动词的助词. 地
        * uz: 接状态词的助词. 着
        * rz: 这位
        * ng: 名词性语素
        * vq: 去过
        * uj: 接形容词的助词. 的
        * rg: 代词性语素
        * mq: 数量词
        * vi: 不及物动词
        * ud: 接副词的助词. 得
        * ug: 连接词语素. 过
        * nrt: 音译人名
        * eng: 英文
        """
        words_with_pos = pseg.cut(' '.join(words))
        return map(lambda x: (x.word, x.flag), words_with_pos)

    @classmethod
    def sent_tokenize(cls, paragraph):
        """
        将一个段落分割成为句子

        :param paragraph: 段落文本
        :return: 返回分割完成后的句子列表
        """
        sentences = cls.__re_sent.split(paragraph)
        ret = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                ret.append(sentence)
        return ret

    @classmethod
    def word_tokenize(cls, sentence, with_pos=False, char_level=False, **kwargs):
        """
        将一个句子分割成为词/标点

        :param sentence: 句子文本
        :param with_pos: 是否需要包含词性, 默认为 False
        :param char_level: 是否是字级别的分词, 默认为 False, 如果是字级别则不存在 pos 信息
        :return: 返回分割完成后的词的列表: 包含词性为 [(word, pos), (word, pos), ...]
        """
        if with_pos:
            if char_level:
                return map(lambda x: (x, None), sentence)
            else:
                words_with_pos = pseg.cut(sentence)
                return map(lambda x: (x.word, x.flag), words_with_pos)
        else:
            if char_level:
                return list(sentence)
            else:
                return jieba.cut(sentence)

    @classmethod
    def lemmatize(cls, word, pos=None):
        """
        依据词和词性简化词 (中文不需要), 所有词均会变成小写.

        :param word: 词
        :param pos: 词性
        :return: 返回简化后的词
        """
        return word.lower()
