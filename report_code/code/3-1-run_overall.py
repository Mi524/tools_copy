from read_config import engine_text,base_dir,input_dir,output_dir, output_draw_dir, startdate, enddate 
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

counter = 0
t1 = time.clock()

#整体部分的计算
print("以下计算程序预计需要1分钟")
#将新的电商数据更新到overall统计表
procedure_list  = ["update_web2overall",
				   "process_overall"]

for p in procedure_list:
	counter += 1 
	sql_procedure = text("call {0} ;".format(p)).execution_options(autocommit=True)
	exec_result = conn.execute(sql_procedure)
	print(counter,"计算：{} 已完成".format(p))


procedure_list  = ['calc_overall',
				   'calc_overall_top6']

for p in procedure_list:
	counter += 1 
	sql_procedure = text("call {0}('{1}');".format(p,enddate)).execution_options(autocommit=True)
	conn.execute(sql_procedure)
	print(counter,"计算：{} 已完成".format(p))

t2 = time.clock()

print('用时 ',round(t2-t1,0))


conn.close()
db.dispose()
