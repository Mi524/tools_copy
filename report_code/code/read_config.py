import os 
import pandas as pd 
import datetime 
from pathlib import Path
from dateutil.relativedelta import relativedelta
from common_utils.os_functions import enter_exit

"""储存基本设置，例如数据库链接信息等"""
def get_enddate(txt_path):
	try:
		with open(txt_path,'r',encoding='utf-8') as file:
			enddate_str = file.read()
			#防止手写的日期格式有问题
			try:
				enddate = pd.to_datetime(enddate_str)
				enddate_str = datetime.datetime.strftime(enddate,'%Y%m%d')
			except :
				enter_exit('日期有错误')
	except :
		enter_exit(f'无法读取到{txt_path}文档，请确认文档在输入数据文件夹')

	return enddate_str 

#链接数据库信息
# engine_text = "mysql+mysqldb://root:VIVO123.@localhost:3306/web_data?charset=utf8mb4"

engine_text = "mysql+mysqldb://data_account:VIVO123.@172.20.178.28:3306/web_data?charset=utf8mb4"

#画图结果存放位置, 确保能获取当前路径
cwd_upper_dir = Path(os.getcwd()).parent
print('当前目录:',cwd_upper_dir)

#code文件夹位置
base_dir = "..\\"
#输入数据的文件夹位置
input_dir = '..\\输入数据'
#故障类别数量文档
fault_phen_dir = '..\\故障类别数量'

#读取计算日期的位置（默认该TXT文档会从售后下载的数据中自动生成）
date_path = os.path.join(input_dir,'提取日期.txt')

#截止日期 1.从提取日期中读 ， 2.自己调试自己改
enddate =  get_enddate(date_path)
enddate = datetime.datetime.strptime(enddate,'%Y%m%d')
startdate = enddate - relativedelta(months=12) + relativedelta(days=1)

enddate_str = datetime.datetime.strftime(enddate,'%Yy%#mm').replace('y','年').replace('m','月')
#数据结果存放位置
output_dir = '..\\输出数据-{}'.format(datetime.datetime.strftime(enddate,'%Yyear%#mmonth').replace('year','年').replace('month','月'))

##之前输出的数据结果, 给画图win32com读取
result_dir = os.path.join(cwd_upper_dir,output_dir.replace('..\\',''))

output_draw_dir = '{}\\输出数据-{}-画图'.format(cwd_upper_dir,enddate_str)


