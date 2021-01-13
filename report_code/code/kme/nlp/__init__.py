# -*- coding: utf-8 -*-
"""
将设定语言的 nlp 处理对象实例化, 并且添加对应的函数, 用户不用考虑对象, 只需要调用即可
"""
from __future__ import unicode_literals

from .nlp_eng import NlpEng
from .nlp_zhs import NlpZhs


def word_tokenize(language='en', *args, **kwargs):
    if language == 'en':
        return NlpEng.word_tokenize(*args, **kwargs)
    elif language == 'zh':
        return NlpZhs.word_tokenize(*args, **kwargs)
    else:
        raise ValueError('invalid language ' + language)


def sent_tokenize(language='en', *args, **kwargs):
    if language == 'en':
        return NlpEng.sent_tokenize(*args, **kwargs)
    elif language == 'zh':
        return NlpZhs.sent_tokenize(*args, **kwargs)
    else:
        raise ValueError('invalid language ' + language)


def pos_tag(language='en', *args, **kwargs):
    if language == 'en':
        return NlpEng.pos_tag(*args, **kwargs)
    elif language == 'zh':
        return NlpZhs.pos_tag(*args, **kwargs)
    else:
        raise ValueError('invalid language ' + language)


def lemmatize(language='en', *args, **kwargs):
    if language == 'en':
        return NlpEng.lemmatize(*args, **kwargs)
    elif language == 'zh':
        return NlpZhs.lemmatize(*args, **kwargs)
    else:
        raise ValueError('invalid language ' + language)
