from xlsxwriter.workbook import Workbook
from xlsxwriter.exceptions import FileCreateError
from collections import defaultdict
import sys
import xlrd
import re
import os 
import time 
import math
from common_utils.os_functions import choose_file,get_require_files

import warnings 
warnings.filterwarnings('ignore')


def choose_sheet_column(file_path):
	"""
	打开文档选择sheeth和column,并且返回一个worksheet内容,方便后面使用
	"""
	print('\nReading Sheet...')
	wb = xlrd.open_workbook(file_path, on_demand=True)
	sheet_names = wb.sheet_names()
	sheet_str_list = [ ' ' + str(i) +'-' + str(x).rstrip('0').rstrip('.') for i,x in enumerate(sheet_names) ]

	if len(sheet_names) == 1 :
		sheet_choose_index = 0
	else:
		print('\n'.join(sheet_str_list))
		sheet_choose_index = input('\n---Please input Sheet Number and press Enter(Default:First sheet): ').strip()
		#打开文档
		if sheet_choose_index == '':
			sheet_choose_index = 0

	choose_index_tag = 0 

	while choose_index_tag < 1:
		try:
			sheet_choose_index = int(sheet_choose_index)
			sheet_choose = sheet_names[sheet_choose_index]
			choose_index_tag += 1 
		except :
			print('Invalid Sheet number!')
			sheet_choose_index = input('\n---Please input Sheet Number and press Enter(Default:First sheet): ').strip()

	#打开工作簿 读取列
	ws = wb.sheet_by_name(sheet_choose)
	columns = [x.value for x in ws.row(0)]

	column_str_list = [ ' ' + str(i) +'-' + str(x).rstrip('0').rstrip('.') for i,x in enumerate(columns)]

	if len(columns) == 1 :
		column_choose_index = 0
	else:
		print('\n')
		print('\n'.join(column_str_list))
		column_choose_index = input('\n---Please input the Column Number that needs encrypted（Default:first column):').strip()
		#打开文档
		if column_choose_index == '':
			column_choose_index = 0

	column_choose_index = int(column_choose_index)
	column_choose = columns[column_choose_index]	
	#返回的是xlrd的wb
	return wb,ws,sheet_choose,column_choose


def process_column_values(xlrd_ws,highlight_column):
	"""
	可以自己选处理哪个内容
	"""
	#获取columns
	columns = [x.value for x in xlrd_ws.row(0)]
	#定位第几列需要高亮
	highlight_column_index = columns.index(highlight_column)

	def encode_numbers(content):
		result = ""
		number_counter = 0 

		new_content = str(content)
		for c in new_content:
			if c.isnumeric() == True:
				number_counter += 1
				if number_counter > 3 :
					result += '*'
				else:
					result += c
			else:
				number_counter = 0 
				result += c   
				
		#判断是否纯数字，如果是，后面需要rstrip('.0')
		if type(content) != str :
			return result.rstrip('.0')
		else:
			return result 
	#不取第一行
	highlight_column_list = [encode_numbers(x.value) for x in xlrd_ws.col(highlight_column_index)][1:]

	return highlight_column_list

def write2wb(xlsxwriter_wb,highlight_column_list,highlight_column='Text'):

	new_highlight_name ='{0}(Number Encrypted)'.format(highlight_column)

	#第一个sheet记录高亮关键词结果
	xlsxwriter_ws = xlsxwriter_wb.add_worksheet('Encrypted')
	#第一个sheet表头，只写一列即可,表头标黄色
	xlsxwriter_ws.write(0,0,new_highlight_name)

	total_len = len(highlight_column_list)
	
	for row_index,value in enumerate(highlight_column_list):  #[7743:7745]
		if  (row_index + 1) % 2000 == 0 or (row_index + 1== total_len)  :
			print(' Processing...',row_index+1,'/',total_len)

		xlsxwriter_ws.write(row_index+1,0,value)
	#调整每个列的宽度
	xlsxwriter_ws.set_column(0,0,width = 50)

	return xlsxwriter_wb

def save_xlsxwriter_wb(xlsxwriter_wb,path):
	close_tag = 0
	while close_tag <= 0:
		try:
			xlsxwriter_wb.close()
			close_tag += 1 
		except FileCreateError:
			input('\nFailed to write file!\n  Please Close "{}" Then Press Enter to Continue'.format(path))
	print('\n{0} Saved'.format(path))


def encrypt(path):
	content_path = choose_file(path)
	xlrd_wb,xlrd_ws,sheet_name,highlight_column = choose_sheet_column(content_path)

	new_path = re.match('(.*).(xlsx|xls)$',content_path).group(1) + '_{}_Encrypted.xlsx'.format(highlight_column)

	#获取需要加密的数据列
	highlight_column_list = process_column_values(xlrd_ws,highlight_column)

	xlsxwriter_wb = Workbook(new_path)
	xlsxwriter_wb = write2wb(xlsxwriter_wb,highlight_column_list,highlight_column)

	#传过来只是为了关闭
	xlrd_wb.release_resources()

	save_xlsxwriter_wb(xlsxwriter_wb,new_path)

if __name__ == '__main__':
	encrypt('.\\')

	input("\nPress Enter to Exit")