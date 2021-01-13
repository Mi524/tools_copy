from read_config import engine_text,base_dir,input_dir,startdate, enddate 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
import datetime
import os 
import time 
import warnings
from read_config import engine_text 

print('\n开始计算实销月数据,预计需要3分钟')


db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

counter = 0 
t1 = time.clock()

#需要特殊的参数
procedure_list = ['calc_com_main_model']
#这个计算会调用 calc_com_market_day, calc_com_market_day_comment, calc_com_market_month, calc_com_market_month_comment

for p in procedure_list:
	counter += 1 
	special_procedure_1 = text(f'call {p}("{enddate}");').execution_options(autocommit=True)
	exec_result = conn.execute(special_procedure_1)
	print(counter,"计算：{} 已完成".format(special_procedure_1))

#不需要参数
procedure_list = ['calc_com_model_market_month']

for p in procedure_list:
	counter += 1 
	sql_procedure = text("call {0} ;".format(p)).execution_options(autocommit=True)
	exec_result = conn.execute(sql_procedure)
	print(counter,"计算：{} 已完成".format(p))

t2 = time.clock()

print('用时 ',round(t2-t1,0))

conn.close()
db.dispose()
