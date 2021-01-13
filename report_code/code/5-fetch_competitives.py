from common_utils.os_functions import get_require_files
from common_utils.df_functions import pivot2multi_tables
from common_utils.regex_functions import search_en 
from common_utils.sql_functions import write2table,insert_update_table,get_sql_result
from common_utils.excel_functions import write_multi_tables,save_xlsxwriter_wb,save_xlsxwriter_wb,write_pct_columns
from collections import defaultdict 
from xlsxwriter import Workbook
import datetime 
from dateutil.relativedelta import relativedelta
import pandas as pd 
from pandas.api.types import CategoricalDtype
import numpy as np
import re 
import os 
import sql_sentences
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text 
import warnings

from read_config import engine_text,base_dir,input_dir,output_dir, startdate, enddate 

warnings.filterwarnings('ignore')

def format_header2cn_enddate(df):
	df.columns = [datetime.datetime.strftime(x,'%Yyear%#mmonth').replace('year','年').replace('month','月') for x in df.columns ]
	return df

def fill_months_market(df,period):
	month_period = ['实销{}个月'.format(x) for x in range(1,period+1)]
	#补足6个月数据
	for m in month_period :
		if m not in df.columns:
			df[m] = ''
	df = df.loc[:,month_period]
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

def process_filt_model(filt_model_df):
	"""需要过滤的主力机型"""
	#只读取第一列
	filt_model_df = filt_model_df.iloc[:,0]
	filt_model_list = [x.strip() for x in filt_model_df.tolist()] 
	return filt_model_list

#获取SQL和语句结果部分
def compare_series_sqls(compare_df,conn,startdate,enddate):
	"""OV对比系列,包括月份和半年度的SQL语句"""
	sql_dict = defaultdict(list)  
	#key records sentence, value records brand and series amount
	compare_brands = list(compare_df.columns)[1:]
	#循环需要对比的每一行品牌系列
	for i,row in compare_df.iterrows():
		row_df = compare_df.loc[i,compare_brands]
		brand_compare_list = []

		brand_list, series_list = [], []
		pair_str = ''
		#分别组合每行的品牌和系列
		for brand in compare_brands: 
			series = row_df[brand]
			if series == series or (type(series)==str and series.strip() != ''):
				brand_compare_text = f" (brand = '{brand}' and series = '{series}') "
				brand_compare_list.append(brand_compare_text)
				brand_list.append(brand)
				series_list.append(series)

				pair_str += '-'.join([brand,series]) + '  '

		print('正在提取',pair_str)

		brand_compare_text_all = ' or '.join(brand_compare_list)

		#获取对应的SQL语句
		sql_month = sql_sentences.compare_series(brand_compare_text_all,startdate,enddate)
		sql_half_year,sql_half_year_month_change = sql_sentences.compare_series_half_year(brand_compare_text_all,startdate,enddate)

		#转换结果到DF 
		brand_compare_month_result = get_sql_result(conn,sql_month)
		brand_compare_half_year_result =get_sql_result(conn,sql_half_year)
		brand_compare_half_year_mc_result = get_sql_result(conn,sql_half_year_month_change)

		sql_dict['series_compare_month'].append({'sql': sql_month,
												 'fetchall':brand_compare_month_result,
												 'brand_amount':len(compare_brands),
												 'brand_list':brand_list,
												 'series_list':series_list }) 

		sql_dict['series_compare_half_year'].append({'sql': sql_half_year,
													 'fetchall':brand_compare_half_year_result,
													 'brand_amount':len(compare_brands),
													 'brand_list':brand_list,
													 'series_list':series_list }) 

		sql_dict['series_compare_half_year_mc'].append({'sql': sql_half_year_month_change,
											 'fetchall':brand_compare_half_year_mc_result,
											 'brand_amount':len(compare_brands),
											 'brand_list':brand_list,
											 'series_list':series_list }) 

		sql_dict[''].append


	return sql_dict

def compare_model_sqls(conn,startdate,enddate):
	#以下获取的是主力机型经过过滤后的结果
	sql_dict = defaultdict()
	#这个SQL不需要填入任何参数
	sql_market_month = sql_sentences.compare_model()

	fetchall_result = get_sql_result(conn,sql_market_month)

	sql_dict['sql'] = sql_market_month
	sql_dict['fetchall'] = fetchall_result  #df 格式

	return sql_dict

def compare_model_top_sqls(compare_df,conn,startdate,enddate):
	"""TOP故障主力机型对比需要获取对比的机型列表"""
	sql_dict = defaultdict(list)  
	#key records sentence, value records brand and series amount
	compare_brands = list(compare_df.columns)[1:]
	#循环需要对比的每一行品牌机型
	for i,row in compare_df.iterrows():
		row_df = compare_df.loc[i,compare_brands]
		brand_compare_list = []

		brand_list, model_list = [], []

		pair_str = ''
		#分别组合每行的品牌和系列
		for brand in compare_brands: 
			model = row_df[brand]
			if model == model or (type(model)==str and model.strip() != ''):
				brand_compare_text = f" (brand = '{brand}' and model = '{model}') "
				brand_compare_list.append(brand_compare_text)
				brand_list.append(brand)
				model_list.append(model)

				pair_str += '-'.join([brand,model]) + '  '

		print('正在提取',pair_str)
		brand_compare_text_all = ' or '.join(brand_compare_list)

		model_top_sql_1,model_top_sql_2= sql_sentences.compare_model_top(brand_compare_text_all,startdate,enddate)

		#第一个SQL不返回任何结果，为了把@min_date拿出来
		conn.execute(model_top_sql_1)

		fetchall_result = get_sql_result(conn,model_top_sql_2)
	
		sql_dict['model_top_sql'].append({'sql':model_top_sql_2,
										  'fetchall':fetchall_result,
										  'brand_amount':len(compare_brands),
										  'brand_list':brand_list,
										  'model_list':model_list} ) 

	return sql_dict 

def compare_model_types_sqls(conn,startdate,enddate):
	"""竞品主力机型对比重点管控项"""
	sql_dict = defaultdict()

	sql_market_month = sql_sentences.compare_model_types_market_month()
	sql_nature_month = sql_sentences.compare_model_types_nature_month()

	fetchall_result_market_month  =  get_sql_result(conn,sql_market_month)

	fetchall_result_nature_month	=  get_sql_result(conn,sql_nature_month)

	sql_dict['model_types_market_month'] = {'sql':sql_market_month,
							  				'fetchall':fetchall_result_market_month}

	sql_dict['model_types_nature_month'] = {'sql':sql_nature_month,
							  				'fetchall':fetchall_result_nature_month}

	return sql_dict

#竞品系列 不同品牌 不同价位 对比
def compare_brand_price_sqls(conn,startdate,enddate):
	sql_dict = defaultdict()

	sql_brand_price = sql_sentences.compare_brand_price(startdate,enddate)
	sql_brand_price_types = sql_sentences.compare_brand_price_types(startdate,enddate)

	fetchall_brand_price = get_sql_result(conn,sql_brand_price)
	fetchall_brand_price_types = get_sql_result(conn,sql_brand_price_types)

	sql_dict['brand_price'] = {'sql':sql_brand_price,
							   'fetchall':fetchall_brand_price}

	sql_dict['brand_price_types'] = {'sql':sql_brand_price_types,
							  				'fetchall':fetchall_brand_price_types}

	return sql_dict 


def get_series_model_contains(conn,startdate,enddate):
	"""读取某个品牌某个价位包含什么系列 以及 某个系列包含什么机型"""

	sql_dict = defaultdict()

	sql_brand_series,sql_series_model = sql_sentences.get_series_model_contains(startdate,enddate)
	
	fetchall_brand_series = get_sql_result(conn,sql_brand_series)
	fetchall_series_model = get_sql_result(conn,sql_series_model)

	sql_dict['brand_series'] = {'sql':sql_brand_series,
							   'fetchall':fetchall_brand_series}

	sql_dict['series_model'] = {'sql':sql_series_model,
							  	'fetchall':fetchall_series_model}

	return sql_dict 


def compare_brand_price(sql_dict,save_path,startdate,enddate):
	writer_wb = Workbook(save_path)
	compare_result_df = sql_dict['fetchall']

	#这个是读取的品牌价位包含哪些系列
	additional_df = sql_dict['additional_info']

	compare_result_df = pd.merge(compare_result_df,additional_df,'left',on=['品牌','价格区间'])

	test = compare_result_df.loc[compare_result_df['价格区间'].isna(),:]

	compare_result_df['品牌'] = compare_result_df['品牌'] + ' ' + compare_result_df['系列组合'].fillna('')

	compare_result_df = compare_result_df.drop(['系列组合','系列组合_中文'],axis=1)

	target_list = ['故障类别数量','发帖数量','负向口碑占比'] 

	filt_targets = compare_result_df['价格区间'].unique()

	for filt_target in filt_targets:
		compare_pivot_list = pivot2multi_tables(compare_result_df,index='品牌',columns='月份',
						value_list=target_list,filt_column='价格区间',filt_target=filt_target)

		model_compare_list = [ ]
		for compare_pivot in compare_pivot_list:
			compare_pivot = format_header2cn_enddate(compare_pivot)
			compare_pivot = fill_months_nature(compare_pivot,enddate,12)
			compare_pivot = compare_pivot.fillna(value='')

			model_compare_list.append(compare_pivot)

		sheet_name = filt_target + '卢比'

		write_multi_tables(writer_wb,sheet_name,model_compare_list,direction=0)
 
	save_xlsxwriter_wb(writer_wb,save_path)


def compare_brand_price_types(sql_dict,save_path,startdate,enddate,price_range):

	writer_wb = Workbook(save_path)
	compare_result_df = sql_dict['fetchall']

	#包含有系列 品牌列表
	additional_df = sql_dict['additional_info']

	compare_result_df = pd.merge(compare_result_df,additional_df,'left',on=['品牌','价格区间'])

	compare_result_df['品牌'] = compare_result_df['品牌'] + ' ' + compare_result_df['系列组合'].fillna('')

	compare_result_df = compare_result_df.drop('系列组合',axis=1)

	#限制不同价格
	compare_result_df = compare_result_df.loc[compare_result_df['价格区间']==price_range,:]

	target_list =  ['故障类别数量','发帖数量','负向口碑占比'] 
	filt_targets = ['拍照类','反应慢/卡顿类','网络信号类','使用时间类','系统稳定性','发热类']

	for filt_target in filt_targets:
		compare_pivot_list = pivot2multi_tables(compare_result_df,index='品牌',columns='月份',
							value_list=target_list,filt_column='故障类别',filt_target=filt_target)

		model_compare_list = [ ]
		for compare_pivot in compare_pivot_list:
			compare_pivot = format_header2cn_enddate(compare_pivot)
			compare_pivot = fill_months_nature(compare_pivot,enddate,12)
			compare_pivot = compare_pivot.fillna(value='')

			model_compare_list.append(compare_pivot)

		sheet_name = filt_target.replace('/','|')
		write_multi_tables(writer_wb,sheet_name,model_compare_list,direction=0)

	save_xlsxwriter_wb(writer_wb,save_path)


def compare_model_types_nature_month(sql_dict,save_path,startdate,enddate,filt_model_list=[]):
	"""专门给发热类-自然月写的部分"""

	writer_wb = Workbook(save_path)

	compare_result_df = sql_dict['fetchall']

	#在机型名称包含有系列名称的不要把品牌拼接到机型
	compare_result_df['系列Extra'] = compare_result_df['系列'].apply(lambda x : x.split(' ')[0])
	compare_result_df['机型Extra'] = compare_result_df['机型'].apply(lambda x : x.split(' ')[0])

	model_contain_series_df = compare_result_df.loc[compare_result_df['系列Extra']==compare_result_df['机型Extra'],:]
	model_not_contain_series_df = compare_result_df.loc[compare_result_df['系列Extra']!=compare_result_df['机型Extra'],:]

	model_not_contain_series_df['机型'] = model_not_contain_series_df['品牌'] + ' ' + model_not_contain_series_df['机型']

	compare_result_df = pd.concat([model_contain_series_df,model_not_contain_series_df],axis=0,ignore_index=True)\
							.reset_index(drop=True)

		#过滤机型				
	compare_result_df = compare_result_df.loc[compare_result_df['机型'].isin(filt_model_list)==False,:]

	target_list = ['故障类别数量','发帖数量','负向口碑占比'] 
	filt_targets = ['拍照类','反应慢/卡顿类','网络信号类','使用时间类','系统稳定性','发热类']

	#修改添加
	rate_rank_dict = defaultdict()
	for filt_target in filt_targets :
		rate_rank_df = compare_result_df.loc[compare_result_df['故障类别']==filt_target,['机型','月份','负向口碑占比']]
		rate_rank_df = rate_rank_df.sort_values(by=['机型','月份','负向口碑占比'],ascending=[True,False,False])
		rate_rank_df = rate_rank_df.drop_duplicates(subset=['机型'],keep='first')
		rate_rank_df = rate_rank_df.rename({'负向口碑占比':'排序'},axis=1).drop('月份',axis=1)
		rate_rank_dict[filt_target] = rate_rank_df

	for filt_target in filt_targets:

		compare_pivot_list = pivot2multi_tables(compare_result_df,index='机型',columns='月份',
						value_list=target_list,filt_column='故障类别',filt_target=filt_target)

		model_compare_list = [ ]
		for compare_pivot in compare_pivot_list:
			compare_pivot = format_header2cn_enddate(compare_pivot)
			compare_pivot = fill_months_nature(compare_pivot,enddate,6)
			compare_pivot = compare_pivot.fillna(value='')

			#获取索引名称方便merge
			compare_pivot_index_name = compare_pivot.index.name
			compare_pivot.index.name = '机型'
			compare_pivot = compare_pivot.reset_index()
			compare_pivot = pd.merge(compare_pivot,rate_rank_dict[filt_target],'left',on='机型')
			compare_pivot = compare_pivot.set_index(keys=['机型'])
			compare_pivot.index.name = compare_pivot_index_name
			compare_pivot = compare_pivot.sort_values(by='排序',ascending=False).drop('排序',axis=1)

			model_compare_list.append(compare_pivot)

		sheet_name = filt_target.replace('/','|')

		write_multi_tables(writer_wb,sheet_name,model_compare_list,direction=0)

	save_xlsxwriter_wb(writer_wb,save_path)


def compare_model_types_market_month(sql_dict,save_path,startdate,enddate,filt_model_list=[]):
	"""#发热类需要另外提取一个自然月份的"""
	writer_wb = Workbook(save_path)

	compare_result_df = sql_dict['fetchall']

	compare_result_df = compare_result_df.reset_index(drop=True)

	#在机型名称包含有系列名称的不要把品牌拼接到机型
	compare_result_df['系列Extra'] = compare_result_df['系列'].apply(lambda x : x.split(' ')[0])
	compare_result_df['机型Extra'] = compare_result_df['机型'].apply(lambda x : x.split(' ')[0])

	model_contain_series_df = compare_result_df.loc[compare_result_df['系列Extra']==compare_result_df['机型Extra'],:]
	model_not_contain_series_df = compare_result_df.loc[compare_result_df['系列Extra']!=compare_result_df['机型Extra'],:]

	model_not_contain_series_df['机型'] = model_not_contain_series_df['品牌'] + ' ' + model_not_contain_series_df['机型']

	compare_result_df = pd.concat([model_contain_series_df,model_not_contain_series_df],axis=0,ignore_index=True)\
							.reset_index(drop=True)

	#过滤机型				
	compare_result_df = compare_result_df.loc[compare_result_df['机型'].isin(filt_model_list)==False,:]
	#特别记录一个负向占比的排名，写入的时候按照排名倒序写入
	
	target_list = ['累计故障类别数量','累计发帖数量','累计负向口碑占比'] 
	filt_targets = ['拍照类','反应慢/卡顿类','网络信号类','使用时间类','系统稳定性','发热类']


	#修改添加
	rate_rank_dict = defaultdict()
	for filt_target in filt_targets :

		rate_rank_df = compare_result_df.loc[compare_result_df['故障类别']==filt_target,['机型','实销月数','累计负向口碑占比']]
		rate_rank_df = rate_rank_df.sort_values(by=['机型','实销月数','累计负向口碑占比'],ascending=[True,False,False])
		rate_rank_df = rate_rank_df.drop_duplicates(subset=['机型'],keep='first')
		rate_rank_df = rate_rank_df.rename({'累计负向口碑占比':'排序'},axis=1).drop('实销月数',axis=1)
		rate_rank_dict[filt_target] = rate_rank_df

	for filt_target in filt_targets:

		compare_pivot_list = pivot2multi_tables(compare_result_df,index='机型',columns='实销月数',
						value_list=target_list,filt_column='故障类别',filt_target=filt_target)

		model_compare_list = [ ]
		for compare_pivot in compare_pivot_list:
			compare_pivot = fill_months_market(compare_pivot,6)
			compare_pivot = compare_pivot.fillna(value='')

			#获取索引名称方便merge
			compare_pivot_index_name = compare_pivot.index.name
			compare_pivot.index.name = '机型'
			compare_pivot = compare_pivot.reset_index()
			compare_pivot = pd.merge(compare_pivot,rate_rank_dict[filt_target],'left',on='机型')
			compare_pivot = compare_pivot.set_index(keys=['机型'])
			compare_pivot.index.name = compare_pivot_index_name
			compare_pivot = compare_pivot.sort_values(by='排序',ascending=False).drop('排序',axis=1)

			model_compare_list.append(compare_pivot)

		sheet_name = filt_target.replace('/','|')

		write_multi_tables(writer_wb,sheet_name,model_compare_list,direction=0)

	save_xlsxwriter_wb(writer_wb,save_path)

# 以下是写入结果部分
def series_compare_month(sql_dict,save_path,startdate,enddate):
	"""提取出系列对比数据后将结果拆分成各个系列 写入不同的sheet"""
	writer = pd.ExcelWriter(save_path, engine='xlsxwriter')
	writer_wb = writer.book 


	sql_dict_list = sql_dict['series_compare_month']

	for info_dict in sql_dict_list:
		#保存每个sheet的三个表格
		compare_result_list = []

		sql = info_dict['sql']
		result_num = info_dict['brand_amount']  #it's a number
		brand_list = info_dict['brand_list']  
		series_list = info_dict['series_list']  

		#每个系列对比写入不同的sheet
		sheet_name = '与'.join(series_list)
		sheet_name = sheet_name.replace(' Series','系列')
		
		compare_result_df = info_dict['fetchall']

		if compare_result_df.empty:  #返回空列表,无结果
			print('没有找到完整系列数据！')
		else:
			#转换日期为表头
			compare_result_df['系列'] = compare_result_df['品牌'] + ' ' +  compare_result_df['系列'] 
			#故障类别  发帖数量 负向口碑占比  分别提取
			target_list = ['故障类别数量','发帖数量','负向口碑占比']
			compare_pivot_list = pivot2multi_tables(compare_result_df,index='系列',columns='日期',value_list=target_list)

			for compare_pivot in  compare_pivot_list:
				compare_pivot =  format_header2cn_enddate(compare_pivot)

				#需要将残缺的12个月列补充
				compare_pivot = fill_months_nature(compare_pivot,enddate,12)
				compare_pivot = compare_pivot.fillna(value='')

				compare_result_list.append(compare_pivot)

		write_multi_tables(writer_wb,sheet_name,compare_result_list,0)

	save_xlsxwriter_wb(writer_wb,save_path)

def series_compare_half_year(sql_dict,save_path,startdate,enddate):
	"""提取出系列对比数据后将结果拆分成各个系列 写入不同的sheet"""
	writer = pd.ExcelWriter(save_path, engine='xlsxwriter')
	writer_wb = writer.book 

	sql_dict_list = sql_dict['series_compare_half_year']

	for info_dict in sql_dict_list:
		#保存每个sheet的三个表格
		compare_result_list = []

		sql = info_dict['sql']
		result_num = info_dict['brand_amount']  #it's a number
		brand_list = info_dict['brand_list']  
		series_list = info_dict['series_list']  

		#保存机型的品牌信息
		brand_dict = defaultdict(str)
		for b, s in zip(brand_list,series_list):
			brand_dict[b+' '+s] = b 

		#每个系列对比写入不同的sheet
		sheet_name = '与'.join(series_list)
		sheet_name = sheet_name.replace(' Series','系列')
		
		compare_result_df = info_dict['fetchall']

		if compare_result_df.empty :  #返回空列表,无结果
			pass 
		else:
			#转换日期为表头
			compare_result_df['系列'] = compare_result_df['品牌'] + ' ' +  compare_result_df['系列'] 
			#需要记录V的系列的故障排名
			v_fault_rank_df = compare_result_df.loc[compare_result_df['品牌']=='vivo','故障类别']
			v_fault_rank_df = v_fault_rank_df.reset_index(drop=True).reset_index()

			#提取结果字段包括 品牌 系列 故障类别 故障类别数量 发帖数量 负向口碑占比  分别提取
			target_list = ['故障类别数量','发帖数量','负向口碑占比'] 

			compare_pivot_list = pivot2multi_tables(compare_result_df,index='故障类别',columns='系列',value_list=target_list)

			for target, compare_pivot in zip(target_list, compare_pivot_list):
				v_fault_rank_df.columns = ['故障类别排名',target]
				#通过故障排名关联转置的结果
				compare_pivot = pd.merge(compare_pivot,v_fault_rank_df,'left',on=target)
				compare_pivot = compare_pivot.sort_values(by=['故障类别排名',target])

				compare_pivot = compare_pivot.drop('故障类别排名',axis=1)

				if '发帖数量' in compare_pivot.columns[0] :
					compare_pivot = compare_pivot.fillna(method='ffill')
				else:
					compare_pivot = compare_pivot.fillna(value=0)

				#V的放在前面一列
				columns_original = list(compare_pivot.columns) 
				columns_brands = [brand_dict.get(x,None) for x in compare_pivot.columns] 

				#找出前面的None位置
				none_num = len([ x for x in columns_brands if x==None])
				if 'vivo' in columns_brands :
					v_index = columns_brands.index('vivo')
					v_target = columns_original.pop(v_index)
					columns_original.insert(none_num,v_target)

				compare_pivot = compare_pivot.loc[:,columns_original]
				compare_pivot = compare_pivot.fillna('')

				compare_result_list.append(compare_pivot)

		write_multi_tables(writer_wb,sheet_name,compare_result_list,1)

	save_xlsxwriter_wb(writer_wb,save_path)

 #加入半年部分
def series_compare_half_year_mc(sql_dict,save_path,startdate,enddate):
	"""提取出系列对比数据后将结果拆分成各个系列 写入不同的sheet"""
	writer = pd.ExcelWriter(save_path, engine='xlsxwriter')
	writer_wb = writer.book 

	sql_dict_list = sql_dict['series_compare_half_year_mc']

	for info_dict in sql_dict_list:
		sql = info_dict['sql']
		result_num = info_dict['brand_amount']  #it's a number
		brand_list = info_dict['brand_list']  
		series_list = info_dict['series_list']  

		#保存机型的品牌信息
		brand_dict = defaultdict(str)
		for b, s in zip(brand_list,series_list):
			brand_dict[b+' '+s] = b 

		#每个系列对比写入不同的sheet
		sheet_name = '与'.join(series_list)
		sheet_name = sheet_name.replace(' Series','系列')
		
		compare_result_df = info_dict['fetchall']

		if compare_result_df.empty :  #返回空列表,无结果
			pass 
		else:
			#转换日期为表头
			compare_result_df['系列'] = compare_result_df['品牌'] + ' ' +  compare_result_df['系列'] 

			#提取结果字段包括 品牌 系列 故障类别 故障类别数量 发帖数量 负向口碑占比  分别提取
			target_list = ['负向口碑占比'] 

			#获取VIVO最近一个月排名TOP10的故障
			v_top15 = compare_result_df.loc[(compare_result_df['品牌']=='vivo')&(compare_result_df['月份']==enddate),:]
			#前10v_top15_2
			v_top15_1 = v_top15.sort_values(by=['负向口碑占比'],ascending=False).iloc[:10,:]
			#防止重点管控项没有在前10		
			fault_type_important = ['拍照类','反应慢/卡顿类','网络信号类','使用时间类','系统稳定性','发热类']	

			v_top15_2 = v_top15.loc[(v_top15['故障类别'].isin(fault_type_important))|(v_top15.index.isin(v_top15_1.index)),:]

			filt_targets = v_top15_2['故障类别'].unique()

			model_compare_list = [ ]
			for filt_target in filt_targets:
				compare_pivot_list = pivot2multi_tables(compare_result_df,index='系列',columns='月份',
								value_list=target_list,filt_column='故障类别',filt_target=filt_target)

				for compare_pivot in compare_pivot_list:
					compare_pivot = format_header2cn_enddate(compare_pivot)
					compare_pivot = fill_months_nature(compare_pivot,enddate,12)
					compare_pivot = compare_pivot.fillna(value='')

					model_compare_list.append(compare_pivot)

			#系列循环保存
			write_multi_tables(writer_wb,sheet_name,model_compare_list,direction=0)
		 
	save_xlsxwriter_wb(writer_wb,save_path)


def process_pivot(model_compare_df,target_list):

	model_compare_list = [ ]
	for target in target_list:
		compare_pivot_list = pivot2multi_tables(model_compare_df,index='机型',columns='实销月数',
					value_list=target_list)

	for compare_pivot in compare_pivot_list:
		compare_pivot = fill_months_market(compare_pivot,6)
		compare_pivot = compare_pivot.fillna(value='')

		model_compare_list.append(compare_pivot)

	return model_compare_list

def model_compare(sql_dict,save_path,startdate=None,enddate=None,filt_model_list=[]):
	"""分别写入OV和所有竞品机型"""
	writer = pd.ExcelWriter(save_path)
	writer_wb = writer.book 

	compare_result_df = sql_dict['fetchall']

	#在机型名称包含有系列名称的不要把品牌拼接到机型
	compare_result_df['系列Extra'] = compare_result_df['系列'].apply(lambda x : x.split(' ')[0])
	compare_result_df['机型Extra'] = compare_result_df['机型'].apply(lambda x : x.split(' ')[0])

	model_contain_series_df = compare_result_df.loc[compare_result_df['系列Extra']==compare_result_df['机型Extra'],:]
	model_not_contain_series_df = compare_result_df.loc[compare_result_df['系列Extra']!=compare_result_df['机型Extra'],:]

	model_not_contain_series_df['机型'] = model_not_contain_series_df['品牌'] + ' ' + model_not_contain_series_df['机型']

	compare_result_df = pd.concat([model_contain_series_df,model_not_contain_series_df],axis=0,ignore_index=True)\
							.reset_index(drop=True)

	#过滤不要的机型
	compare_result_df = compare_result_df.loc[compare_result_df['机型'].isin(filt_model_list)==False,:]

	ov_compare_df = compare_result_df.loc[compare_result_df['品牌'].isin(['OPPO','vivo']),:]

	target_list = ['累计故障类别数量','累计发帖数量','累计负向口碑占比'] 

	compare_pivot_list = process_pivot(compare_result_df,target_list)
	ov_compare_pivot_list = process_pivot(ov_compare_df,target_list)

	rate_rank_df = compare_result_df.loc[:,['机型','实销月数','累计负向口碑占比']]
	rate_rank_df = rate_rank_df.sort_values(by=['机型','实销月数','累计负向口碑占比'],ascending=[True,False,False])
	rate_rank_df = rate_rank_df.drop_duplicates(subset=['机型'],keep='first')
	rate_rank_df = rate_rank_df.rename({'累计负向口碑占比':'排序'},axis=1).drop('实销月数',axis=1)

	#修改，添加最后一个周期的排序
	model_compare_list = [ ]
	for compare_pivot in compare_pivot_list:
		compare_pivot = fill_months_market(compare_pivot,6)
		compare_pivot = compare_pivot.fillna(value='')

		#获取索引名称方便merge
		compare_pivot_index_name = compare_pivot.index.name
		compare_pivot.index.name = '机型'
		compare_pivot = compare_pivot.reset_index()
		compare_pivot = pd.merge(compare_pivot,rate_rank_df,'left',on='机型')
		compare_pivot = compare_pivot.set_index(keys=['机型'])
		compare_pivot.index.name = compare_pivot_index_name
		compare_pivot = compare_pivot.sort_values(by='排序',ascending=False).drop('排序',axis=1)

		model_compare_list.append(compare_pivot)

	#修改，添加最后一个周期的排序
	ov_model_compare_list = [ ]
	for compare_pivot in ov_compare_pivot_list:
		compare_pivot = fill_months_market(compare_pivot,6)
		compare_pivot = compare_pivot.fillna(value='')

		#获取索引名称方便merge
		compare_pivot_index_name = compare_pivot.index.name
		compare_pivot.index.name = '机型'
		compare_pivot = compare_pivot.reset_index()
		compare_pivot = pd.merge(compare_pivot,rate_rank_df,'left',on='机型')
		compare_pivot = compare_pivot.set_index(keys=['机型'])
		compare_pivot.index.name = compare_pivot_index_name
		compare_pivot = compare_pivot.sort_values(by='排序',ascending=False).drop('排序',axis=1)

		ov_model_compare_list.append(compare_pivot)

	write_multi_tables(writer_wb,'OV主力机型',ov_model_compare_list,direction=0)
	write_multi_tables(writer_wb,'主力机型',model_compare_list,direction=0)

	save_xlsxwriter_wb(writer_wb,save_path)


def model_compare_top(sql_dict,save_path,startdate,enddate,filt_model_list=[ ]):
	writer = pd.ExcelWriter(save_path)
	writer_wb = writer.book 

	sql_dict_list = sql_dict['model_top_sql']

	for info_dict in sql_dict_list:
		#保存每个sheet的三个表格
		compare_result_list = []

		sql = info_dict['sql']
		result_num = info_dict['brand_amount']  #it's a number
		brand_list = info_dict['brand_list']  
		model_list = info_dict['model_list']  

		#每个系列对比写入不同的sheet
		sheet_name = '与'.join(model_list)
		
		compare_result_df = info_dict['fetchall']

		#保存机型的品牌信息
		brand_dict = defaultdict(str)
		for b, m in zip(brand_list,model_list):
			brand_dict[m] = b 

		if compare_result_df.empty :  #返回空列表,无结果
			print('没有找到任何数据！')
		else:
			#机型后面写上天数
			compare_result_df['机型'] = compare_result_df['机型'] + '(' + compare_result_df['实销天数'].astype(str) + '天)'
			#需要记录V的系列的故障排名
			v_fault_rank_df = compare_result_df.loc[compare_result_df['品牌']=='vivo','故障类别']
			v_fault_rank_df = v_fault_rank_df.reset_index(drop=True).reset_index()

			#提取结果字段包括 品牌 系列 故障类别 故障类别数量 发帖数量 负向口碑占比  分别提取
			target_list = ['故障类别数量','发帖数量','负向口碑占比'] 
			compare_pivot_list = pivot2multi_tables(compare_result_df,index='故障类别',columns='机型',value_list=target_list)

			for target, compare_pivot in zip(target_list, compare_pivot_list):
				v_fault_rank_df.columns = ['故障类别排名',target]
				#通过故障排名关联转置的结果
				compare_pivot = pd.merge(compare_pivot,v_fault_rank_df,'left',on=target)
				compare_pivot = compare_pivot.sort_values(by=['故障类别排名',target])

				compare_pivot = compare_pivot.drop('故障类别排名',axis=1)

				if '发帖数量' in compare_pivot.columns[0]:
					compare_pivot = compare_pivot.fillna(method='ffill')
				else:
					compare_pivot = compare_pivot.fillna(value=0).copy()

				#V的放前面
				#机型后面加了实销日
				columns_original = list(compare_pivot.columns )

				new_brand_dict = defaultdict(str)
				for m,b in brand_dict.items():
					for c in columns_original:
						if m.lower() == c.lower().split('(')[0] :
							new_brand_dict[c] = brand_dict[m]

				columns_brands = [new_brand_dict.get(x,None) for x in compare_pivot.columns] 

				#找出前面的None位置
				none_num = len([ x for x in columns_brands if x==None])
				if 'vivo' in columns_brands :
					v_index = columns_brands.index('vivo')
					v_target = columns_original.pop(v_index)
					columns_original.insert(none_num,v_target)

				compare_pivot = compare_pivot.loc[:,columns_original]

				compare_pivot = compare_pivot.fillna('')
				compare_result_list.append(compare_pivot)

		write_multi_tables(writer_wb,sheet_name,compare_result_list,1)

	save_xlsxwriter_wb(writer_wb,save_path)


def write_series_model_contains(price_series_contains_df,series_model_contains_df,save_path):
	"""写入各价位包含哪些系列和"""
	writer = pd.ExcelWriter(save_path)
	writer_wb = writer.book 

	#各价位包含的系列
	price_series_contains_df = price_series_contains_df.loc[:,['价格区间','品牌','系列组合_中文','机型组合']]
	price_series_contains_df = price_series_contains_df.rename({'系列组合_中文':'系列','机型组合':'机型'},axis=1)

	#vivo排第一个
	brand_rank = ['vivo','OPPO','samsung','xiaomi']
	brand_type = CategoricalDtype(categories=brand_rank,ordered=True)
	price_series_contains_df['品牌'] = price_series_contains_df['品牌'].astype(brand_type)

	price_series_contains_df = price_series_contains_df.sort_values(by=['价格区间','品牌'])

	write_pct_columns(writer_wb,'各价位包含的系列+机型',price_series_contains_df,pct_columns=[],content_columns=['机型'])

	#各系列包含的机型
	series_model_contains_df = series_model_contains_df.rename({'机型组合':'机型'},axis=1)
	series_model_contains_df['品牌'] = series_model_contains_df['品牌'].astype(brand_type)

	series_model_contains_df = series_model_contains_df.sort_values(by=['品牌','系列'])

	write_pct_columns(writer_wb,'各品牌各系列包含的机型',series_model_contains_df,pct_columns=[],content_columns=['机型'])

	save_xlsxwriter_wb(writer_wb,save_path)


#每次计算新的一个月数据即可
def get_startdate(enddate,month=12):
	startdate = datetime.datetime.strptime(enddate,'%Y%m%d') - relativedelta(months=month) + relativedelta(days=1)
	startdate = datetime.datetime.strftime(startdate,'%Y%m%d')
	return startdate
	

"""获取结果表数据并写入文档"""

require_table_list = ['品牌系列机型对比表']

require_table_dict = get_require_files(base_dir,require_table_list)

series_compare_path = require_table_dict['品牌系列机型对比表']

#输入起始时间
# enddate = '20200201'
# enddate = datetime.datetime.strptime(enddate,'%Y%m%d')
# startdate = enddate - relativedelta(months=12) + relativedelta(days=1)
# startdate = datetime.datetime.strftime(startdate,'%Y%m%d')

print('提取区间：',startdate,enddate)
print('')

output_dir = '..\\输出数据-{}'.format(datetime.datetime.strftime(enddate,'%Yyear%#mmonth').replace('year','年').replace('month','月'))

db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

series_compare_path_month_path = os.path.join(output_dir,'4-OV对比-月度.xlsx')
series_compare_path_half_year_path = os.path.join(output_dir,'4-OV对比-半年度.xlsx')
series_compare_path_half_year_mc_path = os.path.join(output_dir,'4-OV对比-半年度趋势.xlsx')

model_compare_path = os.path.join(output_dir,'5-主力机型.xlsx')
model_compare_top_path = os.path.join(output_dir,'6-OV机型TOP故障对比.xlsx')

model_compare_types_market_month_path = os.path.join(output_dir,'7-主力机型故障类别-实销月.xlsx')
model_compare_types_nature_month_path = os.path.join(output_dir,'8-主力机型故障类别-自然月.xlsx')

compare_brand_price_path = os.path.join(output_dir,'9-竞品系列-不同价位.xlsx')

series_model_contains_path = os.path.join(output_dir,'报告填充数据-各价位包含系列和机型.xlsx')

#读取需要对比的系列和主力机型
series_compare_file = pd.ExcelFile(series_compare_path)
sheets_property = series_compare_file.book.sheets()

#需要读取对比信息的部分
for s in sheets_property:
	if 'OV系列对比' in s.name :
		series_compare_df = series_compare_file.parse(s.name)
		#获取SQL句子等信息
		sql_dict = compare_series_sqls(series_compare_df,conn,startdate,enddate) 

		series_compare_month(sql_dict,series_compare_path_month_path,startdate,enddate)
		series_compare_half_year(sql_dict,series_compare_path_half_year_path,startdate,enddate)

		series_compare_half_year_mc(sql_dict,series_compare_path_half_year_mc_path,startdate,enddate)

	if 'OV机型对比' in s.name:
		model_compare_df = series_compare_file.parse(s.name)
		sql_dict = compare_model_top_sqls(model_compare_df,conn,startdate,enddate)
		model_compare_top(sql_dict,model_compare_top_path,startdate,enddate)

	if '主力机型过滤' in s.name:
		filt_model_df = series_compare_file.parse(s.name)
		filt_model_list = process_filt_model(filt_model_df)
		#获取SQL句子等信息
		sql_dict = compare_model_sqls(conn,startdate,enddate)
		model_compare(sql_dict,model_compare_path,startdate,enddate,filt_model_list)
		#竞品机型 6个故障类别 
		sql_dict = compare_model_types_sqls(conn,startdate,enddate)

		sql_dict_1 = sql_dict['model_types_nature_month']
		sql_dict_2 = sql_dict['model_types_market_month']

		compare_model_types_market_month(sql_dict_2,model_compare_types_market_month_path,startdate,enddate,filt_model_list)
		compare_model_types_nature_month(sql_dict_1,model_compare_types_nature_month_path,startdate,enddate,filt_model_list)

#不需要读取对比信息的部分

#竞品 不同价位,  这个的品牌字段 需要填充哪些系列
sql_series_model_dict = get_series_model_contains(conn,startdate,enddate) 
sql_dict = compare_brand_price_sqls(conn,startdate,enddate)

sql_dict_1 = sql_dict['brand_price']
sql_dict_2 = sql_dict['brand_price_types']

#两边都是需要写入这个
price_series_contains_df = sql_series_model_dict['brand_series']['fetchall']
series_model_contains_df = sql_series_model_dict['series_model']['fetchall']

sql_dict_1['additional_info'] = price_series_contains_df
sql_dict_2['additional_info'] = price_series_contains_df

compare_brand_price(sql_dict_1,compare_brand_price_path,startdate,enddate)

price_ranges =  ['小于10K','10K-20K','20K-35K','35K及以上']

for price_range in price_ranges :
	save_path = os.path.join(output_dir,'10-竞品系列-TOP故障-{}.xlsx'.format(price_range))
	compare_brand_price_types(sql_dict_2,save_path,startdate,enddate,price_range)


#将各品牌不同价位包含的系列和机型写入
write_series_model_contains(price_series_contains_df,series_model_contains_df,series_model_contains_path)

conn.close()
db.dispose()