
"""检查全部数据的  机型价格 + 是否在报告中 +  上市价格"""
import pandas as pd 
import re 
import os 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from common_utils.os_functions import enter_exit
from common_utils.sql_functions import write2table 
from read_config import engine_text,base_dir,input_dir,output_dir, output_draw_dir, startdate, enddate,fault_phen_dir
import datetime 
import time 
import warnings
warnings.filterwarnings('ignore')

"""不用输入截止日期,将新的文档放入故障现象数量文件夹即可"""

def last_day_of_month(any_day,time_format = None):
	if time_format is not None:
		any_day = datetime.strptime(any_day,time_format)

	next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
	return next_month - datetime.timedelta(days=next_month.day)


def write_fault2sql(fault_phen_pathes,conn):
	usecols = ['_id','model_id','source_content_id','website_id',
		   'brand','model_name','Series','time','故障现象','故障类别',
		   '上市时间','上市价格','价格区间']

	rename_dict = {'Series':'series','故障现象':'fault_phen','time':'comment_time',
				  '故障类别':'fault_type','上市时间':'launch_date',
				  '上市价格':'launch_price','价格区间':'price_range',
				  '年':'comment_year','月':'comment_month',
				  'model_name':'model','Correct standard_model':'model_name'}

	not_null_cols = ['_id','model_id','brand','model','series','comment_time','fault_phen','fault_type',
					'launch_date','launch_price','price_range']

	fault_df_list = [ ] 
	for f_path in fault_phen_pathes:
		print('正在读取',f_path)
		fault_df = pd.read_excel(f_path)

		#先尝试把其他机型可能的不同名称变成统一的model_name
		fault_df = fault_df.rename({'Correct standard_model':'model_name',
											'机型':'model_name',
											'机型名称':'model_name',
											'model':'model_name',
											'修正的机型名称':'model_name'
											},axis=1)
		for u in usecols:
			if u not in fault_df.columns :
				enter_exit("**缺少必要字段：{} 不能写入**".format(u))
			if fault_df[u].dtype == str:
				fault_df[u] = fault_df[u].str.strip()
				
		print('\n  正在根据"是否包含在口碑报告中"字段删除非报告数据\n  (最好提前把不包含在口碑报告中的数据手动删除)')

		if '是否包含在口碑报告中' in fault_df.columns:
			fault_df = fault_df.loc[fault_df['是否包含在口碑报告中'].str.strip().apply(lambda x: True if x[0]=='是' else False)==True,:]

		fault_df = fault_df.loc[:,usecols]
		fault_df = fault_df.rename(rename_dict,axis=1)

		#检查字段是否有空 + 保持字符型字段两边不包含空格
		for column in not_null_cols: 
			check_non_df = fault_df.loc[fault_df[column].isna(),:]
			fault_df[column] = fault_df[column].apply(lambda x : x.strip() if type(x)==str else x )

			if not check_non_df.empty :
				enter_exit("{}字段有空值".format(column))

		start_position = datetime.datetime.strftime(fault_df['comment_time'].min(),'%Y-%m-%d')
		end_position = datetime.datetime.strftime(fault_df['comment_time'].max(),'%Y-%m-%d')

		#确认是否写入，如果是回车，否的话就关掉窗口
		input('\n   共读取到从{}至{}共 {} 条数据(包含在口碑报告中)\n\
			  回车即确认写入数据库(否则关闭该窗口)'.format(start_position,end_position,len(fault_df)))
		print('开始写入...')

		t1 =  time.clock()

		fault_df['enddate'] =  fault_df['comment_time'].apply(lambda x: last_day_of_month(x))
		#去掉model内的品牌
		fault_df['model'] = fault_df['model']\
					.apply(lambda x :re.sub(pattern='(samsung|OPPO|vivo|xiaomi) ',repl='',string=x,flags=re.I))

		#防止机型前后带个空格
		fault_df['model'] = fault_df['model'].apply(lambda x: x.strip())

		fault_df = merge_report_fault_type(fault_df)
		fault_df['comment_year'] = fault_df['comment_time'].dt.year 
		fault_df['comment_month'] = fault_df['comment_time'].dt.month 

		#先写入数据库
		write2table(engine_text,fault_df,'ecommerce_data',how='mysql_load')

		print('mysql已写入',f_path)
		t2 = time.clock()
		print('用时',round(t2-t1,0),'秒\n')

def merge_report_fault_type(fault_df):

	#映射TOP故障的部分
	top_dict = {
		'反应慢/卡顿类':'反应慢/卡顿类',
		'发热类':'发热类',
		'网络信号类':'网络信号类',
		'拍照类':'拍照类',
		'使用时间类':'使用时间类',
		'开关机类':'系统稳定性',
		'重启类':'系统稳定性',
		'死机类':'系统稳定性',
		'无':'无'
	}

	top_rank_dict = {
		'反应慢/卡顿类':1,
		'发热类':2,
		'网络信号类':3,
		'拍照类':4,
		'使用时间类':5,
		'开关机类':6,
		'重启类':6,
		'死机类':6,
		'无': 100 
	}

	top_match_df = pd.DataFrame(data=top_dict.items(),columns=['fault_type','fault_type_report'])
	top_rank_match_df = pd.DataFrame(data=top_rank_dict.items(),columns = ['fault_type','fault_type_rank'])

	top_df = pd.merge(top_match_df,top_rank_match_df,'left',on='fault_type')

	#匹配出报告用到的系统稳定性字段
	fault_df = pd.merge(fault_df,top_df,'left',on=['fault_type'])
	#填充空值方便统计
	fault_df['fault_type_report'] = fault_df['fault_type_report'].fillna(value=fault_df['fault_type'])
	fault_df['fault_type_rank'] = fault_df['fault_type_rank'].fillna(value=99)

	return fault_df

fault_phen_pathes = os.listdir(fault_phen_dir)
fault_phen_pathes = [os.path.join(fault_phen_dir,x) for x in fault_phen_pathes if '~$' not in x and '故障类别数量' in x ]

#链接数据库
db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

write_fault2sql(fault_phen_pathes,conn)

conn.close()
db.dispose()