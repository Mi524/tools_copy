"""计算竞品部分"""
from read_config import engine_text,base_dir,input_dir,startdate, enddate 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
import datetime
import os 
import warnings
import time 

db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

#从电商评论数据计算所有的数量
#计算报告类别的数量
#计算精确到机型的发帖数量
#计算精确到机型的结果（注意需要先计算记性发帖数量才能算这个故障数量,涉及right join逻辑）
#精确到系列的结果
#精确到品牌的结果
#各个价位段 各个品牌 TOP6 重点管控项 负向口碑占比 
#计算实销日

#设置计算的月份跨度，一般算12个月的既可（填入12-1 = 11个月,date_sub原因），偶尔需要提取所有历史数据要算12个月以上的数据
months_range = 23

counter = 0
t1 = time.clock()
#电商数据的计算，跑完整个过程需要大概15分钟

#基础计算表,最耗时间的两个表
print('以下计算程序预计需要2分钟')
procedure_list = [ 'calc_com_all_phens',
				   'calc_com_comment_num']


for p in procedure_list:
	counter += 1 
	sql_procedure = text("call {0}('{1}',{2});".format(p,enddate,months_range)).execution_options(autocommit=True)
	exec_result = conn.execute(sql_procedure)
	print(counter,"计算：{} 已完成".format(p))

#需要两个日期参数
procedure_list  = [
				   'calc_com_all_types',
				   'calc_com_model',
				   'calc_com_model_types',
				   'calc_com_series',
				   'calc_com_series_types',
				   'calc_com_brand',
				   'calc_com_brand_types',
				   'calc_com_price',
				   'calc_com_price_types',
				   'calc_com_series_half_year_types']

for p in procedure_list:
	counter += 1 
	sql_procedure = text("call {0}('{1}',{2});".format(p,enddate,months_range)).execution_options(autocommit=True)
	exec_result = conn.execute(sql_procedure)
	print(counter,"计算：{} 已完成".format(p))

t2 = time.clock()
print('用时 ',round(t2-t1,0))


conn.close()
db.dispose()



