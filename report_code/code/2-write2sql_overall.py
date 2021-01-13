from common_utils.os_functions import get_require_files,last_day_of_month
from common_utils.df_functions import remove_duplicate_columns,\
process_enddate,delete_unnamed_behind,stack_list_column
from common_utils.regex_functions import search_en 
from common_utils.sql_functions import write2table,insert_update_table
import datetime 
import pandas as pd 
import re 
import os 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text 
from read_config import engine_text,base_dir,input_dir,output_dir, output_draw_dir, startdate, enddate,fault_phen_dir

import warnings

warnings.filterwarnings('ignore')

"""意见反馈、呼叫中心 新的数据写入MYSQL"""
def read_ifSum(if_sum_path):
	"""将是否纳入统计的字段更新到overall_sum_types表"""
	statistic_wb = pd.ExcelFile(if_sum_path)
	read_dict = {
		'售后':1,
		'意见反馈':1,
		'呼叫中心':1,
		'互联网':1
	}

	df_list = [ ]
	#将纳入统计和不纳入统计的数据更新到整体表 vivo_overall
	for sheet,i in read_dict.items():
		try:
			df = statistic_wb.parse(sheet)
		except :
			print('尝试打开Sheet"{}"出现错误!')
			continue 
		df_list.append(df)

	if_sum_df = pd.concat(df_list,axis=0,ignore_index=True)
	if_sum_df = if_sum_df.rename({'来源':'source_name','故障类别':'fault_type','是否纳入统计':'if_sum'},axis=1)

	return if_sum_df 

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

def process_shipments(shipment_path):
	"""销量部分:注意这个表因为机型比较混乱，所以只读取EXCEL计算的结果，最后的4行数据"""
	shipment_df = pd.read_excel(shipment_path)
	#删掉unnamed部分
	shipment_df = delete_unnamed_behind(shipment_df)

	usecols_index = [i for c,i in zip(shipment_df.columns,range(len(shipment_df.columns))) \
					if type(c) !=str or len([x for x in ['国家','呼叫中心'] if x in c]) <=0 ]

	shipment_df = shipment_df.iloc[:,usecols_index]

	first_column  = list(shipment_df.columns)[0]
	shipment_df = shipment_df.rename({first_column:'source_name'},axis=1)

	#只保留半年销量的结果
	shipment_df = shipment_df.loc[shipment_df['source_name']\
				.apply(lambda x:type(x)==str and '最近半年销量' in x)]

	shipment_df = pd\
			.melt(shipment_df,id_vars=['source_name'],var_name=['enddate'],value_name='shipment_half_year')

	shipment_df = shipment_df.loc[shipment_df['shipment_half_year'].isna()==False,:].reset_index(drop=True)

	#提取里面适用的渠道
	source_set = set(['意见反馈','售后','网络'])
	re_source = '(意见反馈|售后|网络)'
	
	shipment_df['source_name'] = shipment_df['source_name'].apply(lambda x : re.findall(re_source,x)) 
	#叠起
	shipment_df = stack_list_column(shipment_df,'source_name')
	#确保每个渠道都有对应的半年销量
	lack_source = set(shipment_df['source_name'].unique()) - source_set
	if lack_source :
		print('找不到渠道"{0}"的半年销量数据，请确保“最近半年销量（{0}）类似格式”在文档第一列'.format('及'.join(lack_source)))
	
	sort_columns =  ['source_name','enddate','shipment_half_year']
	shipment_df = shipment_df.sort_values(by=sort_columns,ascending=[True,True,False],na_position='last')

	shipment_df = shipment_df.drop_duplicates(subset=['source_name','enddate'])

	shipment_df = process_enddate(shipment_df)
	shipment_df['shipment_half_year'] = shipment_df['shipment_half_year'].fillna(value=0)

	return shipment_df 

def process_overall(aftersale_path,callcenter_feedback_dict,if_sum_path):
	#先处理售后数据，里面含有截止日期
	aftersale_df = pd.read_excel(aftersale_path)
	aftersale_df = aftersale_df.loc[aftersale_df['enddate'].isna()==False,:]
	report_enddate = aftersale_df['enddate'][0]

	aftersale_df['source_name'] = '售后'

	#意见反馈+呼叫中心, 截止日期从售后提取
	callcenter_feedback_list = [ ]
	for source,file in callcenter_feedback_dict.items():
		df = pd.read_excel(file,header=2)
		df = df.iloc[:,1:]
		first_column  = list(df.columns)[0]
		df = df.loc[df[first_column].isna()==False,:]
		df = df.T
		df = df.reset_index()
		df.columns = ['fault_type','fault_type_num']
		df['source_name'] = source
		df['enddate'] = report_enddate
		callcenter_feedback_list.append(df)

	#合并售后 + 意见反馈 + 呼叫中心数据
	overall_df = pd.concat([aftersale_df]+callcenter_feedback_list, axis=0,ignore_index=True)
	overall_df = merge_report_fault_type(overall_df,top_rank_path)

	overall_df['fault_type'] = overall_df['fault_type'].str.upper() 

	#提取if_sum字段
	if_sum_df = read_ifSum(if_sum_path)
	if_sum_df['fault_type'] = if_sum_df['fault_type'].str.upper() 
	if_sum_df = if_sum_df.loc[:,['source_name','fault_type','if_sum']]

	overall_df = pd.merge(overall_df,if_sum_df,'left',on=['source_name','fault_type'])

	return overall_df


require_tables = ['报告故障类别映射表',
				  'vivo整体纳入统计的类别',
				  '计算填充关联表']

require_tables_input = ['印度VOC呼叫中心数据',
				  		'印度VOC意见反馈数据',
				  		'印度售后失效数据BI-透视',
				  		'销量机型']

require_file_dict = get_require_files(base_dir,require_tables)

require_tables_input_dict = get_require_files(input_dir,require_tables_input)

if_sum_path = require_file_dict['vivo整体纳入统计的类别']
top_rank_path = require_file_dict['报告故障类别映射表']
#电商数据计算用到的匹配填充表,包括 basic_all_brands
basic_table_path = require_file_dict['计算填充关联表']

callcenter_feedback_dict = {'呼叫中心':require_tables_input_dict['印度VOC呼叫中心数据'],
			                '意见反馈':require_tables_input_dict['印度VOC意见反馈数据']}

aftersale_path = require_tables_input_dict['印度售后失效数据BI-透视']
shipment_path = require_tables_input_dict['销量机型']


overall_df = process_overall(aftersale_path,callcenter_feedback_dict,if_sum_path)
shipment_df = process_shipments(shipment_path)

insert_update_table(engine_text,overall_df,'overall')
print('已更新vivo整体表')
#出货量
insert_update_table(engine_text,shipment_df,'shipments')
print('已更新销量表')