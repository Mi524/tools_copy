"""将机型信息写入数据库"""
from common_utils.os_functions import get_require_files,enter_exit
from common_utils.df_functions import remove_duplicate_columns
from common_utils.regex_functions import search_en 
import pandas as pd 
import re 
import os 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text 
import warnings
from read_config import engine_text,base_dir,input_dir,output_dir, result_dir, output_draw_dir, startdate, enddate 

warnings.filterwarnings('ignore')

"""写入产品信息表到MYSQL"""

def process_model_table(model_info_df):
	#只读取model_info_df表里面的机型和对应上市时间字段
	model_info_df = remove_duplicate_columns(model_info_df)

	model_info_df.columns = [search_en(x).strip().lower().replace('\n',' ') \
							 if type(x) == str and search_en(x) != None \
							 else x.strip().replace('\n',' ') for x in model_info_df.columns]

	model_info_df['model'] = model_info_df['model'].apply(lambda x:x.strip() if type(x)==str else x )
	return model_info_df 

#2 -- 写入产品信息表
base_dir = '..\\输入数据'

require_table_list = ['产品信息表']
require_table_dict = get_require_files(base_dir,require_table_list)

model_info_path = require_table_dict['产品信息表']

print(model_info_path)

model_info_df = pd.read_excel(model_info_path)

model_info_df = process_model_table(model_info_df)

model_info_df.columns = [x.replace(' ','_') for x in model_info_df.columns]


model_info_df = remove_duplicate_columns(model_info_df) 

rename_dict = {'country/region':'region',
			  'cpu':'cpu_name',
			  'status':'current_status',
			  '是否包含在口碑报告中':'if_report_contains',
			  '口碑报告中的价格区间':'price_range'}

info_usecols = ['brand','series','model','if_report_contains',
				'price_range','launch_date','launch_price',
				'display','front_camera','rear_camera',
				'ram','rom','cpu_name','cpu_alias','battery',
				'product_configuration_time','information_for',
				'current_status','region']


model_info_df = model_info_df.rename(rename_dict,axis=1)

rename_dict_reverse = dict([(x,y) for y,x in rename_dict.items()])

h = lambda x, y : x.replace(x,y[x])

tag = 0 
for u in info_usecols:
	if u not in model_info_df.columns:
		print('产品信息表缺失字段：{},原始文档名称：{}, 需要补充再继续'.format(u,h(u,rename_dict_reverse)))
		tag + 1 

if tag > 0 :
	enter_exit('需要补充以上字段,再继续')


model_info_df = model_info_df.loc[:,info_usecols]	

#去掉不包含在口碑报告中的
report_contains_condition = model_info_df['if_report_contains']\
				.apply(lambda x: True if type(x)==str and re.search('^是',x)!=None else False)

model_info_df = model_info_df.loc[report_contains_condition,:]

#去掉机型里面的OPPO 和 Samsung
brand_list = ['vivo','OPPO','xiaomi','samsung']

def replace_brand(input_word):
	for b in brand_list:
		input_word = input_word.replace(b,'').strip()
	return input_word

model_info_df['model'] = model_info_df['model'].apply(lambda x : replace_brand(x))

#链接数据库
db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

#先将原来的数据清空
safe_update_statement = text("set sql_safe_updates=0;")
truncate_statement = text("truncate {}".format('basic_model_info'))

conn.execute(safe_update_statement)
conn.execute(truncate_statement)

model_info_df.to_sql('basic_model_info',con=conn,if_exists='append',index=False)

print('产品信息表已更新')

conn.close()
db.dispose()