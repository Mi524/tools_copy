from read_config import engine_text,base_dir,input_dir,startdate, enddate 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
import datetime
import os 
import time 
import warnings

print('\n开始计算分析数据,预计需要1分钟')

db = create_engine(engine_text,poolclass=NullPool)
conn = db.connect()

counter = 0 
t1 = time.clock()

#需要运行的分析表计算
procedure_list  = ['ana_overall_month_change',
				   'ana_series_month_change',     
				   'ana_series_half_year',
				   'ana_price_month_change',
				   'ana_model_market_month_change',
				   'ana_model_abnormal_change'
				 								] 
				 								
for p in procedure_list:
	counter += 1 
	sql_procedure = text("call {0}('{1}');".format(p,enddate)).execution_options(autocommit=True)
	exec_result = conn.execute(sql_procedure)
	print(counter,"分析表计算过程：{} 已完成".format(p))

t2 = time.clock()

print('用时 ',round(t2-t1,0))

conn.close()
db.dispose()
