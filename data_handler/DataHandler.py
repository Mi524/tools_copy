# -*- coding: utf-8 -*-
import gc
import re
import sys
import os
import time
import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import hashlib
from collections import defaultdict, Counter
from common_utils.sequence_functions import list_diff_outer_join, lcs, filter_lcs
from common_utils.os_functions import *
from common_utils.df_functions import *
from common_utils.excel_functions import write_format_columns
from common_utils.regex_functions import replace_re_special, replace_punctuations
from common_utils.decorator_functions import df_row_num_decorator, get_run_time
from common_utils.data_handle_func import *
from common_utils.sql_functions import close_sql_connection
from common_utils.data_handle_sheet_func import Handler
from common_utils.config_table import ConfigReader
import sqlite3

import warnings

warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)

from pandas.core.index import MultiIndex

class DataHandler(object):

    def __init__(self, require_file_dir, input_dir, table_dict, *args, **kwargs):

        self.require_file_dir = os.path.abspath(require_file_dir)
        self.input_dir = os.path.abspath(input_dir)
        self.table_dict = table_dict

        # 创建默认的结果检查数据
        self.result_checking_dir = kwargs.get(
            'result_checking_dir', '.\\result_checking')
        check_create_new_folder(self.result_checking_dir)

        # 创建处理数据类的
        self.handler = Handler(self.require_file_dir,
                               self.input_dir, self.table_dict)

    @catch_and_print
    def process_data(self):
        # 以下合并结果后，会得到一个handler.save_name(获取数据日期的最大最小值 作为结果输出）
        complete_header_df, success_sheet_df = self.handler.concat_data()
        min_max_date_range = self.handler.min_max_date_range

        # 先写入合并后的结果
        # write_format_columns(os.path.join(self.result_checking_dir,'Original input data concat result.xlsx'),
        # 					   complete_header_df,'concat_result')

        # 保留一个原始的结果,后面可能在match的部分做匹配（提取预警的详情--数据先经过了分组计算过滤出预警结果再获取原始数据）
        original_complete_header_df = complete_header_df.copy()
        return_dict = {}

        checking_result_list = []
        checking_result_sheet_names = []
        output_file_type = 'xlsx'

        if not complete_header_df.empty:
            print('')
            process_counter = -1
            for process, table in self.table_dict.items():
                process_counter += 1
                process_lower = process.lower().strip()

                if process not in ['complete_header_df', 'target_cn_columns']:
                    print(f'[{process_counter}] {process} config processing...')

                if 'standardization' in process_lower and not table.empty:
                    complete_header_df, partial_match_failed_df = self.handler.standardize_columns(
                        complete_header_df, table)
                    checking_result_list.append(partial_match_failed_df)
                    checking_result_sheet_names.append('Fail to standardize')

                if 'split' in process_lower and not table.empty:
                    complete_header_df = self.handler.split_columns(
                        complete_header_df, table)

                if 'match' in process_lower and not table.empty:
                    complete_header_df, not_match_df = self.handler.match_columns(
                        complete_header_df, table)
                    checking_result_sheet_names.append('Fail to match')
                    checking_result_list.append(not_match_df)

                if'deduplication' in process_lower and not table.empty:
                    complete_header_df = self.handler.drop_duplicate_data(
                        complete_header_df, table)

                # 先做过滤再输出结果
                if 'filter' in process_lower and not table.empty:
                    complete_header_df = self.handler.filter_columns(
                        complete_header_df, table)

                if 'extraction' in process_lower and not table.empty:
                    complete_header_df = self.handler.regex_extraction(
                        complete_header_df, table)

                # 用作统计规则
                if 'time process' in process_lower and not table.empty:
                    complete_header_df = self.handler.calc_time(
                        complete_header_df, table)

                if 'statistic group' in process_lower and not table.empty:
                    # 不同的sheet里面必须确保填入的分组完全相同
                    complete_header_df = self.handler.process_statistic_groups(
                        complete_header_df, table)

                if 'calculations' in process_lower and not table.empty:
                    complete_header_df = self.handler.process_calculations(
                        complete_header_df, table)

                if 'pivot' in process_lower and not table.empty:
                    complete_header_df = self.handler.pivot_table(
                        complete_header_df, table)

                if 'connection' in process_lower and not table.empty:
                    # connection config sheet have to be before sql/write to db sheet
                    #不会返回任何结果,conn, db,已经在函数中传进handler的属性
                    complete_header_df = self.handler.exec_connection(
                        complete_header_df, table)

                if 'sql' in process_lower and not table.empty:
                    # transaction设置等待半小时 60 * 60 * 30 = 1800000 miliseconds
                    complete_header_df = self.handler.exec_sql(
                        complete_header_df, table)

                if 'write to db' in process_lower and not table.empty:
                    # 写入数据表操作不会返回任何结果
                    complete_header_df = self.handler.exec_write_to_db(
                        complete_header_df, table)

                if 'fill&sort' in process_lower and not table.empty:
                    complete_header_df = self.handler.fill_and_sort_columns(
                        complete_header_df, table)
                    # 最后一列是输出格式
                    output_file_type = str(table.values[0][-1])
                    if output_file_type.lower().strip() != 'csv':
                        output_file_type = 'xlsx'

            checking_result_list.append(success_sheet_df)
            checking_result_sheet_names.append('Success read amount')

            result_dict = {
                'complete_header_df': complete_header_df,
                'checking_result_list': checking_result_list,
                'checking_result_sheet_names': checking_result_sheet_names,
                'output_file_type': output_file_type,
                'min_max_date_range': min_max_date_range
            }

        else:
            enter_exit(f'No valid data found in {self.input_dir}!')

        # 必须关闭链接
        close_sql_connection(self.handler.conn, self.handler.db)

        return result_dict


if __name__ == '__main__':

    require_file_dir = '.\\require_tables'
    input_dir = '.\\input_data'
    output_dir = '.\\output_data'

    # 参数传入配置文件夹
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=str, required=False,
                        help='config folder dir', default='')
    parser.add_argument('-i', type=str, required=False,
                        help='input folder dir', default='')
    parser.add_argument('-o', type=str, required=False,
                        help='output folder dir', default='')

    args = parser.parse_args()

    # 看是否传入了输入输出参数
    if args.i.strip() != '':
        input_dir = args.i.strip()
    if args.o.strip() != '':
        output_dir = args.o.strip()

    config_file_dir = args.c.strip()

    if config_file_dir == '':
        # 如果没有传入参数，就选择配置文件夹
        config_file_dir = choose_folder('.\\', 'config')

    # config_file_dir = '.\\config_calc_words(Global)'
    # config_file_dir = '.\\config_calc_amount(Global)'
    # config_file_dir = '.\\config_calc_amount(Global) - OSversion'
    # config_file_dir = '.\\config_calc_amount(Global) - day calculations'

    try:
        config_table_path_list = sorted(
            [x for x in os.listdir(config_file_dir) if '~$' not in x])
    except FileNotFoundError:
        enter_exit(f"{config_file_dir} doesn't exists ! ")

    config_list = ['mapping',
                   'standardization',
                   'split',
                   'match',
                   'deduplication',
                   'fill&sort',
                   'filter',
                   'extraction',
                   # 以下是统计的配置表
                   'time process',
                   'statistic groups',
                   'calculations',
                   'pivot',
                   # 通过sqlite3在connect(":memory:")生成临时表做计算
                   'connection',
                   'sql',
                   'write to db']

    if not config_table_path_list:
        enter_exit(f'No config files are found in {config_file_dir}! ')

    # 刷新一遍配置文件
    config_file_dir = str(Path(config_file_dir).absolute())

    print('')
    refresh_configs([os.path.join(config_file_dir, x) for x in config_table_path_list])

    counter = 0
    result_df_list = []
    sheet_name_list = []

    # 为什么不先读取所有数据文件然后再统一进行config的处理？ 
    # -- 因为每个config文档的字段映射可能不同，所以必须循环读取
    for config_table_name in config_table_path_list:
        counter += 1
        print(f'\nConfig file {counter}:', config_table_name)

        print(f'Reading files in {input_dir}')

        # 读取配置表
        table_reader = ConfigReader(config_file_dir=config_file_dir,
                                    config_table_name=config_table_name,
                                    config_list=config_list)

        table_dict = table_reader.get_config_tables(if_walk_path=False)

        # 数据处理部分
        data_handler = DataHandler(table_dict=table_dict,  # 配置表
                                   input_dir=input_dir,  # 输入数据
                                   require_file_dir=require_file_dir)  # 数据处理用到的所有表

        result_dict = data_handler.process_data()

        result_df = result_dict['complete_header_df']
        checking_result_list = result_dict['checking_result_list']
        checking_result_sheet_names = result_dict['checking_result_sheet_names']
        output_file_type = result_dict['output_file_type']
        min_max_date_range = result_dict['min_max_date_range']

        # 因为save_name需要包含数据里面的最大最小日期，所以放在循环里面处理
        sheet_name = get_save_sheet_name(config_table_name)

        result_df_list.append(result_df)
        sheet_name_list.append(sheet_name)

    save_name = get_save_name(output_dir, config_file_dir, min_max_date_range)

    save_results(save_name=save_name, result_df_list=result_df_list,
                 sheet_name_list=sheet_name_list, checking_result_list=checking_result_list,
                 checking_result_sheet_names=checking_result_sheet_names, output_file_type=output_file_type)

    # 如果没有传入参数，是手动选择的配置文件则回车再退出, 传入的参数贼直接退出，方便bat文件处理
    if args.c.strip() == '':
        enter_exit('')
