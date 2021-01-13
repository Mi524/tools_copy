from common_utils.os_functions import get_require_files
from common_utils.df_functions import pivot2multi_tables
from common_utils.regex_functions import search_en 
from common_utils.sql_functions import write2table,insert_update_table,get_sql_result 
from common_utils.excel_functions import write_multi_tables,save_xlsxwriter_wb,save_xlsxwriter_wb,write_pct_columns
from collections import defaultdict 
import datetime 
from dateutil.relativedelta import relativedelta
import pandas as pd 
import numpy as np
import re 
import os 
import sql_sentences
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text 
import warnings

from xlsxwriter import Workbook

from read_config import engine_text,base_dir,input_dir,output_dir, output_draw_dir, startdate, enddate 

"""获取分析表"""
print('提取分析表区间：',startdate,enddate)
print('')

db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

print('正在提取 vivo整体分析表')
overall_month_change_name = '故障类别影响比重'
overall_month_change_sql = sql_sentences.ana_overall_month_change(startdate,enddate)
overall_month_change_df = get_sql_result(conn,overall_month_change_sql)

#1.提取详细基础故障现象数据
print('正在提取 基础现象数据-自然月')
all_phens_sql = sql_sentences.ana_all_com_phens(startdate,enddate)

all_phens_df = get_sql_result(conn,all_phens_sql)

print('正在提取 基础现象数据-半年度')
half_year_phens_sql = sql_sentences.ana_half_year_phens(startdate,enddate)
half_year_phens_df =  get_sql_result(conn,half_year_phens_sql)

print('正在提取 基础现象数据-实销月')
model_market_month_phens_sql = sql_sentences.ana_market_month_phens(startdate,enddate)
model_market_month_phens_df = get_sql_result(conn,model_market_month_phens_sql)

#2.提取分析用表	
print("正在提取 分析表-系列自然月")
series_month_change_sqls = sql_sentences.ana_series_month_change(startdate,enddate)

series_month_change_df_list = [ ]
series_month_change_df_names = ['机型影响比重','类别影响比重','机型+类别影响比重']

for sql in series_month_change_sqls:
	series_month_change_df = get_sql_result(conn,sql)
	series_month_change_df_list.append(series_month_change_df)

#2 
print("正在提取 分析表-价位自然月")
price_month_change_sqls =  sql_sentences.ana_price_month_change(startdate,enddate)

price_month_change_df_list = [ ]
price_month_change_df_names =  ['机型影响比重','类别影响比重','机型+类别影响比重']

for sql in price_month_change_sqls:
	price_month_change_df = get_sql_result(conn,sql)
	price_month_change_df_list.append(price_month_change_df)

#3 
print("正在提取 分析表-系列半年度")
series_half_year_change_df_name  = '机型影响比重'
series_half_year_change_sql = sql_sentences.ana_series_half_year_change(startdate,enddate)
series_half_year_change_df = get_sql_result(conn,series_half_year_change_sql)

#4 
print("正在提取 分析表-机型实销月")
model_market_month_df_name = '类别影响比重'
model_market_month_change_sql = sql_sentences.ana_model_market_month_change(startdate,enddate)
model_market_month_change_df = get_sql_result(conn,model_market_month_change_sql)

#5
print('正在提取 分析表-机型异常变动')
model_abnormal_change_names = ['机型异常变动(自然月)','机型异常变动(实销月)']
model_abnormal_change_sql_1,model_abnormal_change_sql_2 = sql_sentences.ana_model_abnormal_change(startdate,enddate)
model_abnormal_change_df_1 = get_sql_result(conn,model_abnormal_change_sql_1)
model_abnormal_change_df_2 = get_sql_result(conn,model_abnormal_change_sql_2)

#统一写入文档
overall_month_change_path = os.path.join(output_dir,"分析表-1-vivo整体自然月变动.xlsx")
basic_data_save_path = os.path.join(output_dir,"分析表-2-故障现象明细(自然月+半年度+实销月).xlsx")
series_month_change_path = os.path.join(output_dir,'分析表-3-系列自然月变动.xlsx')
price_month_change_path = os.path.join(output_dir,'分析表-4-价位自然月变动.xlsx')
series_half_year_change_path = os.path.join(output_dir,'分析表-5-系列半年度影响.xlsx')
model_market_month_change_path =  os.path.join(output_dir,'分析表-6-机型实销月变动.xlsx')
model_abnormal_change_path = os.path.join(output_dir,'分析表-7-机型异常变动.xlsx')

basic_df_list = [all_phens_df,half_year_phens_df,model_market_month_phens_df]
basic_df_names = ['自然月故障现象','半年度故障现象','实销月故障现象']

pct_columns=['反馈率','负向口碑','占比','比重','变动影响','比率','失效率'] 

#1.整体的分析表（判断哪个类别对整体反馈率升高减小贡献最大）
writer_wb = Workbook(overall_month_change_path)
overall_month_change_df = overall_month_change_df.fillna(value='')
write_pct_columns(writer_wb,overall_month_change_name,overall_month_change_df,pct_columns=pct_columns)

save_xlsxwriter_wb(writer_wb,overall_month_change_path)

#2.写入基础故障现象
writer_wb =  Workbook(basic_data_save_path)

for df,name in zip(basic_df_list,basic_df_names):
	df = df.fillna(value='') 
	write_pct_columns(writer_wb,name,df,pct_columns=pct_columns)

save_xlsxwriter_wb(writer_wb,basic_data_save_path)

#3. 系列自然月变动分析表
writer_wb =  Workbook(series_month_change_path)

for df,name in zip(series_month_change_df_list,series_month_change_df_names):
	df = df.fillna(value='')
	write_pct_columns(writer_wb,name,df,pct_columns=pct_columns)

save_xlsxwriter_wb(writer_wb,series_month_change_path)

#4. 价位自然月变动分析表
writer_wb = Workbook(price_month_change_path)

for df,name in zip(price_month_change_df_list,price_month_change_df_names):
	df = df.fillna(value='')
	write_pct_columns(writer_wb,name,df,pct_columns=pct_columns)

save_xlsxwriter_wb(writer_wb,price_month_change_path)

#5. 系列半年变动分析表
writer_wb =  Workbook(series_half_year_change_path)
series_half_year_change_df = series_half_year_change_df.fillna(value='')
write_pct_columns(writer_wb,series_half_year_change_df_name,series_half_year_change_df,pct_columns=pct_columns)

save_xlsxwriter_wb(writer_wb,series_half_year_change_path)

#6. 机型实销月变动分析表
writer_wb =  Workbook(model_market_month_change_path)
model_market_month_change_df = model_market_month_change_df.fillna(value='')
write_pct_columns(writer_wb,model_market_month_df_name,model_market_month_change_df,pct_columns=pct_columns)
save_xlsxwriter_wb(writer_wb,model_market_month_change_path)

#7. 机型异常变动分析表
writer_wb = Workbook(model_abnormal_change_path)
for name, df in zip(model_abnormal_change_names,[model_abnormal_change_df_1,model_abnormal_change_df_2]):
	df = df.fillna(value='')
	write_pct_columns(writer_wb,name,df,pct_columns=pct_columns)
save_xlsxwriter_wb(writer_wb,model_abnormal_change_path)

conn.close()
db.dispose()