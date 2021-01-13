"""计算VIVO整体"""
from common_utils.regex_functions import search_en 
from common_utils.sql_functions import get_sql_result 
from common_utils.excel_functions import autofit_column_width,write_row_format,write_multi_tables,\
										 save_xlsxwriter_wb
from common_utils.df_functions import pivot2multi_tables
import pandas as pd 
import re 
import os 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text 
import sql_sentences
import warnings
import datetime 
from dateutil.relativedelta import relativedelta

from read_config import engine_text,base_dir,input_dir,output_dir, startdate, enddate 

warnings.filterwarnings('ignore')

def format_header2cn_enddate(df):
	df.columns = [datetime.datetime.strftime(x,'%Yyear%#mmonth').replace('year','年').replace('month','月') for x in df.columns ]
	return df

def fill_months_nature(df,enddate,period):
	"""表头填充完整12月"""
	#构建完整的12个月
	months = pd.date_range(end=enddate,periods=period,freq='M')
	months = [datetime.datetime.strftime(x,'%Yyear%#mmonth').replace('year','年').replace('month','月') for x in months]
	for m in months :
		if m not in df.columns :
			df[m] = ''
	df = df.loc[:,months]

	return df

#替换掉表头的月份0，如果开始采用%Y%c月的方式,后面就需要提取出年份和月份的数字再重新排列表头
def process_header(df_list):
	new_df_list = [ ]
	for df in df_list : 
		df =  format_header2cn_enddate(df)
		df = fill_months_nature(df,enddate,12)
		new_df_list.append(df)
	return new_df_list

#每次计算新的一个月数据即可
def get_startdate(enddate,month=12):
	startdate = enddate - relativedelta(months=month) + relativedelta(days=1)
	return startdate

#先是售后部分数据
def overall_main_part(overall_save_path,conn):
	#提取计算结果1 
	sql1 =  sql_sentences.overall(startdate,enddate)
	sql2 =  sql_sentences.overall_top6(startdate,enddate)
	sql3 = sql_sentences.overall_stability(startdate,enddate)
	#fetchall()获取的结果是列表 内嵌 字典的形式
	df_1 = get_sql_result(conn,sql1)
	df_2 = get_sql_result(conn,sql2)
	df_3 = get_sql_result(conn,sql3)

	writer = pd.ExcelWriter(overall_save_path,engine='xlsxwriter')
	writer_wb = writer.book

	sheet_name_1 = '整体负向反馈率趋势图'
	sheet_name_2 = '重点管控项负向反馈量'
	sheet_name_3 = '重点管控项负向反馈率趋势图'
	sheet_name_4 = '系统稳定性负向反馈量'
	sheet_name_5 = '系统稳定性负向反馈率趋势图'

	#将三个列分别存储到三个DF表格
	value_list = ['故障类别数量','半年销量','负向口碑占比']

	df_list_1 = pivot2multi_tables(df_1,index='来源',columns='日期',value_list=value_list,fillna='')

	# #第二个结果，重点管控项
	main_faults_df = df_2.loc[:,['类别排名','故障类别']].sort_values(by='类别排名').drop_duplicates()
	main_faults = main_faults_df['故障类别'].tolist()

	df_2 = df_2.drop(['类别排名'],axis=1)

	value_list = ['故障类别数量','负向口碑占比']

	#区分数量和占比 写入不同sheet
	df_list_2_num = []
	df_list_2_pct = []

	for fault in main_faults:
		df_list_2 = pivot2multi_tables(df_2,index='来源',columns='日期',
				value_list=value_list,filt_column='故障类别',filt_target=fault,fillna=0)

		df_list_2_num.append(df_list_2[0])
		df_list_2_pct.append(df_list_2[1])

	#系统稳定性处理方式和df_2完全相同，以下代码复制粘贴
	#第三个结果，系统稳定性
	main_faults_df = df_3.loc[:,['故障类别']].sort_values(by='故障类别').drop_duplicates()
	main_faults = main_faults_df['故障类别'].tolist()

	df_3 = df_3.drop(['类别排名'],axis=1)

	value_list = ['故障类别数量','负向口碑占比']

	#区分数量和占比 写入不同sheet
	df_list_3_num = []
	df_list_3_pct = []

	for fault in main_faults:
		df_list_3 = pivot2multi_tables(df_3,index='来源',columns='日期',
				value_list=value_list,filt_column='故障类别',filt_target=fault,fillna=0)

		df_list_3_num.append(df_list_3[0])
		df_list_3_pct.append(df_list_3[1])

	#统一处理表头
	df_list_1 = process_header(df_list_1)
	df_list_2_num = process_header(df_list_2_num)
	df_list_2_pct = process_header(df_list_2_pct)
	df_list_3_num = process_header(df_list_3_num)
	df_list_3_pct = process_header(df_list_3_pct)

	#分别写入,负向反馈率写先
	write_multi_tables(writer_wb,sheet_name_1,df_list_1,auto_adjust_pct=True)
	write_multi_tables(writer_wb,sheet_name_3,df_list_2_pct,auto_adjust_pct=True)
	write_multi_tables(writer_wb,sheet_name_5,df_list_3_pct,auto_adjust_pct=True)
	write_multi_tables(writer_wb,sheet_name_2,df_list_2_num,auto_adjust_pct=True)
	write_multi_tables(writer_wb,sheet_name_4,df_list_3_num,auto_adjust_pct=True)

	#保存
	save_xlsxwriter_wb(writer_wb,overall_save_path)

def overall_extra_part(overall_extra_path,conn):
	#提取售后，意见反馈，呼叫中心，互联网的类别统计结果 
	sql0 =  sql_sentences.overall_sources(startdate,enddate)

	#fetchall()获取的结果是列表 内嵌 字典的形式
	df_0 = get_sql_result(conn,sql0)

	writer = pd.ExcelWriter(overall_extra_path,engine='xlsxwriter')
	writer_wb = writer.book 

	extra_sheet_names = ['售后','意见反馈','呼叫中心','互联网']

	for es in extra_sheet_names:
		es_df = df_0.loc[df_0['来源']==es,:]
		#保留一个故障类别的排序
		es_df = es_df.pivot(index='故障类别',columns='日期',values='故障类别数量')

		last_column =  list(es_df.columns)[-1]
		es_df = es_df.sort_values(by=[last_column],ascending=False)
		es_df_sum = es_df.sum(axis=0)
		es_df_sum.name = '总计'

		es_df = es_df.append(es_df_sum)

		es_df =  format_header2cn_enddate(es_df)
		es_df = es_df.fillna(value='')

		write_multi_tables(writer_wb,es,[es_df],direction=0,auto_adjust_pct=True)

	save_xlsxwriter_wb(writer_wb,overall_extra_path)


#准备保存结果

overall_save_path = os.path.join(output_dir,'3-vivo整体.xlsx')
overall_extra_path = os.path.join(output_dir,'3-vivo整体-分渠道分故障.xlsx')


print('提取区间',startdate,'至',enddate)

db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

overall_main_part(overall_save_path,conn)
overall_extra_part(overall_extra_path,conn)


conn.close()
db.dispose()

