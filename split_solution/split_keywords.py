from xlsxwriter.workbook import Workbook
from xlsxwriter.exceptions import FileCreateError
from collections import defaultdict
import sys
import xlrd
import re
import os 
import time 
from common_utils.os_functions import choose_file,choose_sheet_column,get_require_files,enter_exit

import warnings 
warnings.filterwarnings('ignore')

"""把拆分呼叫中心主题字段的方法 拆出来 写到单独的功能脚本"""

def save_xlsxwriter_wb(xlsxwriter_wb,save_path):
	close_tag = 0
	while close_tag <= 0:
		try:
			xlsxwriter_wb.close()
			close_tag += 1 
		except FileCreateError:
			input('\nFailed to write file!\n  Please Close "{0}" Then Press Enter to Continue'.format(save_path))
	print('\n{0} Saved'.format(save_path))


def get_keyword_list(path,re_file_name):
	found_tag = 0 
	while found_tag <= 0:
		try:
			wb = xlrd.open_workbook(path)
			found_tag += 1 
		except FileNotFoundError  :
			input('\n "{0}.xlsx" File Not Found in Current Folder!\n \
Please put the {0}.xlsx to current folder and Press Enter to continue'.format(re_file_name))
			continue 
	ws = wb.sheet_by_index(0)

	#只读取第一列的拆分关键词
	keyword_list = [x for x in ws.col_values(colx=0,start_rowx=0)[1:] if type(x) == str and x.strip() != ''] 

	if keyword_list:
		return keyword_list
	else:
		enter_exit('Cannot read any keyword from the file(first sheet&first column)')

def replace_multi_symbol(symbol,string):
	"""把多个符号替换成单个，比如多个换行符 替换成 一个换行符,replace('\n\n','\n')并不能解决问题"""
	symbol_double = symbol + symbol
	while symbol_double in string:
		string = string.replace(symbol_double,symbol)
	return string

def get_split_text_india(s_pat,text):
	"""
	通过匹配到的match列表，寻找原始text中的index位置,并将原始的text,拆分，返回经过拆分的text,
	text会经过处理变成text_lower
	"""
	text_lower = text.lower()
	match_string_list = re.findall(s_pat,text_lower)
	#记录小写匹配到的index
	m_index_list = []
	m_index_accumulate = 0 
	m_length_accumlate = 0
	for m in match_string_list:
		if m_length_accumlate != 0 :
			m_index_accumulate += m_length_accumlate

		m_index = text_lower.index(m)
		m_index_accumulate += m_index
		m_index_list.append(m_index_accumulate)
		text_lower = text_lower[m_index+len(m):]
		m_length_accumlate = len(m)

	original_match_list = []

	for m_index,m in zip(m_index_list,match_string_list):
		original_match_list.append(text[m_index:m_index+len(m)])

	original_s_pat = '(' + '|'.join(original_match_list)  + ')'
	#注意如果re_pattern里面含有( | | )返回的匹配结果会包括目标单词本身 
	# split_text_lower = re.split(s_pat,text_lower) 
	split_complete_text = re.split(original_s_pat,text) 
	# split_text_lower = [x for x in split_text_lower if x  not in match_string_list]
	split_original_text = [x for x in split_complete_text if x not in original_match_list ]
	#第一个保留，最后一个拆分的solution全部遗弃
	if len(split_original_text) > 2:		
		#拆分的第二个部分会连带着下一段的开始，从第2个元素开始，用换行符分段，保留距离 下一个solution最近的一段
		split_return_text =  split_original_text[1:-1]   
		split_return_text = [x.strip().split('\n') for x in split_return_text]
		split_return_text = [x[-1]+'\n' for x in split_return_text ]
		split_original_text = split_original_text[:1] + split_return_text 
	#如果拆分并去掉建议类关键词后只剩2个部分，第二个部分就是solution ，并且第一个部分字符数大于5，可以直接去掉第二个部分
	elif len(split_original_text) == 2 and len(str(split_original_text[0]).strip()) >= 5 :  
		split_original_text = split_original_text[:-1]
	else:  #如果拆分并去掉关键词后只剩一个部分，该部分也是solution但是由于第一个部分命中的建议关键词在列表被过滤，需要接回来
		split_original_text = split_complete_text
	#返回保留的部分和被拆掉的部分
	split_drop_text = [x for x in split_complete_text if x not in split_original_text]
	return split_original_text,split_drop_text

def split_keywords(keyword_list,text):
	"""
	2019-11-27： 拆分主题字段，对含有solutions等关键词小写的字段进行拆分，并丢弃包括建议的后半段描述
	大小写不敏感,遇到第一个关键词就可以拆分,如果出现了成对的solution，不止一个solution关键词,将倒数最后两个关键词后面部分去掉
	"""
	drop_text = ''
	if type(text) == str:
		text = replace_multi_symbol('\n',text.strip())
		text_lower = text.lower()
		keyword_list = [ x for x in sorted(keyword_list,key= len,reverse=True)]
		#re检查是否存在
		s_pat = '|'.join(keyword_list)
		s_pat = '(' + s_pat  + ')'
		if re.search(s_pat,text_lower) != None:
			#通过suggestion拆分段落 
			split_original_text,split_drop_text = get_split_text_india(s_pat,text)
			#将原来的拆分段落每隔1提取出来再合并即可
			text = '\n'.join(split_original_text).strip()
			drop_text = ''.join(split_drop_text).strip()

	return (text,drop_text)


def split_write(save_path,content_path,keyword_list):
	"""
	可以自己选处理哪个内容
	"""
	xlrd_wb,xlrd_ws,sheet_name,split_column = choose_sheet_column(content_path)

	#获取columns
	columns = [x.value for x in xlrd_ws.row(0)]
	#定位第几列需要拆分
	column_index = columns.index(split_column)
	#不取第一行
	column_series = [x for x in xlrd_ws.col_values(column_index,1)]

	writer_wb = Workbook(save_path)
	writer_ws = writer_wb.add_worksheet('Split_results')

	bold = writer_wb.add_format({'bold':True})
	#写入表头
	headers = ['Split target text','Split drop text']
	writer_ws.write(0,0,headers[0],bold)
	writer_ws.write(0,1,headers[1],bold)

	for i, text in enumerate(column_series):
		target_text, drop_text = split_keywords(keyword_list,text)

		writer_ws.write(i+1,0,target_text)
		writer_ws.write(i+1,1,drop_text)

	writer_ws.set_column(0,0,40)
	writer_ws.set_column(0,1,40)

	save_xlsxwriter_wb(writer_wb,save_path)

	xlrd_wb.release_resources()

require_tables = get_require_files('.\\',['split_keyword'])

keyword_path = require_tables['split_keyword']

keyword_list = get_keyword_list(keyword_path,'Split_keyword')

content_path = choose_file(path=r'.\\')

new_path = re.match('(.*).(xlsx|xls)$',content_path).group(1) + '_Split.xlsx'

split_write(new_path,content_path,keyword_list)


enter_exit('')


