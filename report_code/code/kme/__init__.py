# -*- coding: utf-8 -*-
"""
Keyword Matching Engine
"""
from __future__ import unicode_literals

from .model import Model


def train_model(rule_dir_path, config):
    """
    训练一个模型, 将训练好的模型文件返回

    :param rule_dir_path: 规则文件的路径
    :param config: 存放配置信息的对象
    :return: 返回模型对象
    """
    model = Model.train(rule_dir_path, config)
    return model
