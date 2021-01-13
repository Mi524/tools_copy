from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import time 
import os
from dateutil.relativedelta import relativedelta 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from read_config import engine_text,base_dir,input_dir,startdate, enddate 
import warnings 

warnings.filterwarnings('ignore')

base_dir = '..\\'

#通过最新的一份输出数据文件夹名称获取报告月
file_list = [ x for x in os.listdir(base_dir) if '输出数据' in x and x[-1] == '月']
file_list.sort()

previous_month = file_list[-1].replace('输出数据-','').replace('年','year').replace('月','month')
previous_month = datetime.datetime.strptime(previous_month,'%Yyear%mmonth').date()

current_month = datetime.datetime.strftime(previous_month,"%Yyear%#mmonth").replace('year','年').replace('month','月')

tag1_url = r'file:///D:/My%20Documents/Documents/vchat/NewChatFiles/20191020-%E5%8F%A3%E7%A2%91%E6%8A%A5%E5%91%8A/%E5%8D%B0%E5%BA%A6%E5%8F%A3%E7%A2%91%E6%8A%A5%E5%9B%BE%E8%A1%A8%E7%94%9F%E6%88%90/code/html/tag1.html'
tag2_url = r'file:///D:/My%20Documents/Documents/vchat/NewChatFiles/20191020-%E5%8F%A3%E7%A2%91%E6%8A%A5%E5%91%8A/%E5%8D%B0%E5%BA%A6%E5%8F%A3%E7%A2%91%E6%8A%A5%E5%9B%BE%E8%A1%A8%E7%94%9F%E6%88%90/code/html/tag2.html'
tag3_url = r'file:///D:/My%20Documents/Documents/vchat/NewChatFiles/20191020-%E5%8F%A3%E7%A2%91%E6%8A%A5%E5%91%8A/%E5%8D%B0%E5%BA%A6%E5%8F%A3%E7%A2%91%E6%8A%A5%E5%9B%BE%E8%A1%A8%E7%94%9F%E6%88%90/code/html/tag3.html'

driver = webdriver.Chrome(r"D:\Download\chromedriver.exe")

#分别修改不同的html，第一个部分只修改月份和品牌对比情况
driver.get(tag1_url)

driver.execute_script("var elem = document.getElementById('current-month'); elem.innerHTML='{}'"\
	   .format(current_month))

#读取价位对比表，获取品牌排名
time.sleep(2)

driver.get(tag2_url)

content_part1 = driver.find_element_by_xpath('/html/body/div[1]/div[2]')

model_launch_period = "机型：2017年6月-{}上市的机型".format(current_month)

driver.execute_script("var elem = document.getElementById('model-launch-period'); elem.innerHTML='{}'"\
					 .format(model_launch_period), content_part1)

time.sleep(2)
driver.close()
driver.quit()


