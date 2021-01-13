"""将售后，意见反馈，呼叫中心，互联网数据 历史数据写入MYSQL方便处理
   历史数据一般不用更新，故暂时没写更新的逻辑
"""
from common_utils.os_functions import get_require_files
from common_utils.df_functions import process_enddate,delete_unnamed_behind
from common_utils.sql_functions import insert_update_table
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
import datetime
import os 
import re 
import pandas as pd 
import warnings
from read_config import engine_text,base_dir,input_dir,output_dir, result_dir, output_draw_dir, startdate, enddate 

warnings.filterwarnings('ignore')

def merge_report_fault_type(fault_df,top_rank_path):
	"""读取特殊分类的映射和排序"""
	top_df = pd.read_excel(top_rank_path)
	rename_dict = {
					'原始分类名称':'fault_type',
					'报告分类名称':'fault_type_report',
					'排序':'fault_type_rank'
			}
	top_df = top_df.loc[:,rename_dict.keys()]
	top_df = top_df.rename(rename_dict,axis=1)

	#匹配出报告用到的系统稳定性字段
	fault_df = pd.merge(fault_df,top_df,'left',on=['fault_type'])
	#填充空值方便统计
	fault_df['fault_type_report'] = fault_df['fault_type_report'].fillna(value=fault_df['fault_type'])
	fault_df['fault_type_rank'] = fault_df['fault_type_rank'].fillna(value=99)

	return fault_df

base_dir = '..\\'

require_table_list = ['vivo整体-','报告故障类别映射表']

require_table_dict = get_require_files(base_dir,require_table_list)

overall_path = require_table_dict['vivo整体-']
top_rank_path = require_table_dict['报告故障类别映射表']

print(overall_path)
#整体部分
overall_wb = pd.ExcelFile(overall_path)

#将非原始的类别名称去掉 fault_type_report 字段通过一张匹配表做映射
sheet_name_dict = {'售后':['总计','去掉无故障+空+纯服务+检测无故障','系统稳定性','拍照类','网络信号类'],
				   '意见反馈':['总计','系统稳定性'],
				   '呼叫中心':['总计','系统稳定性']}

sheet_df_list = []

#互联网的数据通过存储过程计算ecommerce_data保存过去
for source,source_not_read in sheet_name_dict.items():
	print("正在读取Sheet:“{}”".format(source))
	try:
		sheet_df = overall_wb.parse(source)
	except :
		print('读取异常，请检查EXCEL文档')

	sheet_df = delete_unnamed_behind(sheet_df)
	#不读取特殊的总计行
	first_column = sheet_df.columns[0]
	sheet_df = sheet_df.rename({first_column:'fault_type'},axis=1)

	sheet_df = sheet_df.loc[(sheet_df['fault_type'].isin(source_not_read)==False)&\
							(sheet_df['fault_type'].apply(lambda x:type(x))==str),:]

	sheet_df['source_name'] = source
	#转置,时间转成列
	sheet_df = pd.melt(sheet_df,id_vars=['source_name','fault_type'],\
			   var_name='enddate',value_name='fault_type_num')

	sheet_df_list.append(sheet_df)
#合并
sheet_df_all = pd.concat(sheet_df_list,axis=0,ignore_index=True)

sheet_df_all = process_enddate(sheet_df_all)

#填充数值0 
sheet_df_all['fault_type_num'] = sheet_df_all['fault_type_num'].fillna(value=0)
sheet_df_all['fault_type'] = sheet_df_all['fault_type'].str.upper()

#写入fault_type_report
sheet_df_all = merge_report_fault_type(sheet_df_all,top_rank_path) 

#写入mysql

#写入历史总体数据记录,需要先清空原来的表
truncate_statement = text("truncate overall;")

insert_update_table(engine_text,sheet_df_all,'overall')

print('已写入整体历史数据(售后+意见反馈+呼叫中心)')
