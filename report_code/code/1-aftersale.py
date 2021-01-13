from common_utils.os_functions import get_require_files,enter_exit,check_create_new_folder
from common_utils.df_functions import remove_duplicate_columns,group_basic_sum,calc_total
from common_utils.regex_functions import partial_match_pct ,search_en
from common_utils.excel_functions import save_excel 
from dateutil.relativedelta import relativedelta
import pandas as pd 
import datetime 
from collections import defaultdict
import re 
import os 
import sys


"""读取输入的售后原始数据，不用填enddate,enddate通过输入的售后的时间的月底决定"""

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  
    return next_month - datetime.timedelta(days=next_month.day)

def process_model_table(model_info_df):
	#只读取model_info_df表里面的机型和对应上市时间字段
	model_info_df = remove_duplicate_columns(model_info_df)

	model_info_df.columns = [search_en(x).strip().lower().replace('\n',' ') \
							 if type(x) == str and search_en(x) != None \
							 else x.strip().replace('\n',' ') for x in model_info_df.columns]

	model_info_df['model'] = model_info_df['model'].apply(lambda x:x.strip() if type(x)==str else x)

	return model_info_df 

def process_aftersale_filt(filt_model_path):
	filt_model_df = pd.read_excel(filt_model_path)
	#只读取第一列
	filt_model_df = filt_model_df.iloc[:,0]
	filt_model_list = [x.strip() for x in filt_model_df.tolist()] 
	return filt_model_list

"""BI导出的售后机型 匹配 产品信息表的机型，获取上市时间信息"""


if __name__ == '__main__':
	#code文件夹位置
	base_dir = "..\\"
	#输入数据的文件夹位置
	input_dir = '..\\输入数据'

	require_table_list = ['印度BI售后失效数据','产品信息表']

	require_table_dict = get_require_files(input_dir,require_table_list,matched_part=None)

	bi_aftersale_path = require_table_dict['印度BI售后失效数据']

	model_info_path = require_table_dict['产品信息表']
	print('找到的机型信息表：',model_info_path)

	require_table_list_1 = ['售后类别统计映射','售后机型过滤']
	require_table_dict_1 = get_require_files(base_dir,require_table_list_1,matched_part=None)

	type_name_path = require_table_dict_1['售后类别统计映射']
	filt_model_path = require_table_dict_1['售后机型过滤']

	#检查有没有找到文件,以及是否以CSV结尾
	if bi_aftersale_path == None :
		enter_exit(f'找不到“印度BI售后失效数据”文档')
	else:
		print('找到的文档：{}'.format(bi_aftersale_path))

	#读取文档
	if re.search('.*.csv$',bi_aftersale_path) != None:
		bi_aftersale_df = pd.read_csv(bi_aftersale_path)
	elif re.search('.*.xlsx$',bi_aftersale_path) != None or re.search('.*.xls$',bi_aftersale_path) != None:
		bi_aftersale_df = pd.read_excel(bi_aftersale_path)

	#存在需要删除的特殊机型
	special_delete_model = process_aftersale_filt(filt_model_path)

	#读取机型表
	model_info_df = pd.read_excel(model_info_path)

	model_info_df = process_model_table(model_info_df)

	model_info_df = model_info_df.loc[model_info_df['brand']=='vivo',['model','launch date']]

	model_info_df = model_info_df.sort_values(by=['model','launch date'],ascending= [False,False])
	model_info_df = model_info_df.drop_duplicates(subset=['model'],keep='first')

	#关联数据
	voc_model_list = model_info_df['model'].unique()

	#用计算匹配度的方式获取 ,确保两边都有i和s
	special_syn_str = ['pro','plus','max','youth','i','s','d']

	bi_aftersale_df['model'] = bi_aftersale_df['机型别名'].apply(lambda x: \
		sorted([partial_match_pct(x,y,special_syn_str) for y in voc_model_list],\
			key=lambda x:x[0],reverse=True)[0][1]
	 if sorted([partial_match_pct(x,y,special_syn_str) for y in voc_model_list],\
	 	    key=lambda x:x[0],reverse=True)[0][0] != 0 else None) 

	bi_aftersale_df = pd.merge(bi_aftersale_df,model_info_df,'left',on=['model'])

	#去掉在不在报告截止日期范围内的机型数据（上市）, 根据bi下载的数据判断报告截止月份
	report_date = bi_aftersale_df['日期'].max()

	print('BI售后数据原始记录{}条'.format(bi_aftersale_df.shape[0]),'最大日期：',report_date)

	enddate = last_day_of_month(pd.to_datetime(report_date))

	#保留往前推2年半期间上市的机型
	# startdate = enddate + relativedelta(months=-(12*2.5)) + relativedelta(days=1)

	#保留从2017年6月开始上市的机型 
	startdate = datetime.datetime.strptime('20170601','%Y%m%d')

	report_model_condition =  (bi_aftersale_df['launch date'] >= startdate) &\
							  (bi_aftersale_df['launch date'] <= enddate) 

	# Y15 32G 是不用删除的，用原来的机型别名判断要不要特别删除
	special_delete_model_condition = bi_aftersale_df['机型别名'].isin(special_delete_model)

	#保留一个被删除的机型
	bi_aftersale_removed = bi_aftersale_df.loc[special_delete_model_condition|(~report_model_condition),:]

	bi_aftersale_df = bi_aftersale_df.loc[report_model_condition,:]
	bi_aftersale_df = bi_aftersale_df.loc[~special_delete_model_condition,:]

	print('保留区间 {} 至 {} 的机型数据:{} 条'.format(datetime.datetime.strftime(startdate,'%Y-%m-%d'),\
										    datetime.datetime.strftime(enddate,'%Y-%m-%d'),
										    bi_aftersale_df.shape[0]))


	bi_aftersale_df = bi_aftersale_df.rename({'model':'信息表机型','launch date':'上市日期'},axis=1).copy()


	bi_aftersale_removed = bi_aftersale_removed.rename({'model':'信息表机型','launch date':'上市日期'},axis=1).copy()


	#分别保存去重后的机型
	single_model_removed = bi_aftersale_removed.loc[:,['机型别名','信息表机型','上市日期']]
	single_model_removed = single_model_removed.drop_duplicates(subset=['机型别名'])


	single_model_saved = bi_aftersale_df.loc[:,['机型别名','信息表机型','上市日期']]
	single_model_saved = single_model_saved.drop_duplicates(subset=['机型别名'])

	single_model_saved['是否相等'] = single_model_saved['机型别名'] == single_model_saved['信息表机型']

	single_model_saved['是否相等'] = single_model_saved['是否相等'].apply(lambda x: '是' if x==True else '否')


	# bi_aftersale_name = bi_aftersale_path.split('\\')[-1].split('.')[0]
		
	save_path = os.path.join(input_dir,"1-印度售后失效数据BI-已过滤机型.xlsx")

	save_path = check_create_new_folder(save_path)

	save_sheets = [bi_aftersale_df,bi_aftersale_removed,single_model_saved,single_model_removed]

	sheet_names =['符合机型区间的数据','被删除的机型数据','符合的机型列表','被删除的机型列表']

	save_excel(save_sheets,save_path,sheet_names)

	print('\n透视数据')

	bi_aftersale_sum = group_basic_sum(bi_aftersale_df,\
					    group_columns=['故障类别名称'],sum_column='失效数量（现象）-当期')

	bi_aftersale_sum = calc_total(bi_aftersale_sum)

	bi_aftersale_sum['故障类别名称'] =  bi_aftersale_sum['故障类别名称']\
						.str.replace('(','（').str.replace(')','）')

	#在前面加入三项 系统稳定性，拍照类，网络信号类,  去掉无故障+空+纯服务+检测无故障
	def append_sum(df,type_name,type_list,exception=False):
		"""将某几个类别合并成一行的统计和"""
		type_df = df.loc[df['故障类别名称'].isin(type_list)!=exception,:]
		type_sum = type_df['数量'].sum()
		df = df.append({'故障类别名称':type_name,'数量':type_sum},ignore_index=True)
		return df

	def get_type_name_dict(type_name_path):
		type_name_df = pd.read_excel(type_name_path)
		#只读取前面两列
		type_name_df = type_name_df.iloc[:,:2]
		#记录一个字典
		type_name_dict = defaultdict(list)
		for i,row in type_name_df.iterrows():
			row_values = [str(x).replace('(','（').replace(')','）') for x in row.values]
			type_name_dict[row_values[0]].append(row_values[1])

		return type_name_dict 

	# type_name_dict = {
	# 	'系统稳定性':['开关机类','死机类','重启类'],
	# 	'拍照类':['后置拍照类','前置拍照类'],
	# 	'网络信号类':['网络信号类（2/3/4G）','网络信号类（5G）'],
	# 	#去掉无故障的部分，而且注意去掉其他有重复的
	# 	'去掉无故障+空+纯服务+检测无故障':['检测无故障','无故障类','空','用户描述无故障（纯服务类）'] \
	# 	+ ['总计','系统稳定性','拍照类','网络信号类']
	# }

	type_name_dict = get_type_name_dict(type_name_path)

	#加入截止时间字段方便后面写OVERALL读取
	bi_aftersale_sum['enddate'] = enddate
	bi_aftersale_sum['enddate'].loc[bi_aftersale_sum['故障类别名称']=='总计'] = None

	for type_name,type_list in type_name_dict.items() :
		exception = False 
		if type_name == '去掉无故障+空+纯服务+检测无故障':
			exception = True
		bi_aftersale_sum = append_sum(bi_aftersale_sum,type_name,type_list,exception=exception)

	#改表头
	bi_aftersale_sum = bi_aftersale_sum.rename({'故障类别名称':'fault_type','数量':'fault_type_num'},axis=1)
	#保存
	save_path = os.path.join(input_dir,"2-印度售后失效数据BI-透视.xlsx")

	save_excel(bi_aftersale_sum,save_path,'透视结果')

	#将读取的截止日期写入TXT文档提供给其他步骤的代码
	enddate_str_txt = os.path.join(input_dir,'提取日期.txt')
	enddate_str = datetime.datetime.strftime(enddate,'%Y-%m-%d')

	with open(enddate_str_txt,'w',encoding='utf-8') as file:
		file.write(enddate_str)
