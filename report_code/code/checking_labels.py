import re
import sys
import os 
from multiprocessing import Pool
import six 
from openpyxl import load_workbook 
# 己方库
from kme import train_model
from kme.result import Results

#数据检查部分的库
import pandas as pd 
from itertools import combinations 
from collections import Counter
from pprint import PrettyPrinter
import time 
from common_utils.df_functions import stack_list_column,calc_total,expand_stacked_column_to_list
from common_utils.sequence_functions import find_sublist_indexes,convert_twolist2dict
from common_utils.sql_functions import get_sql_connection, close_sql_connection
from common_utils.regex_functions import split_wrong_combine

from collections import defaultdict 
#数据连接
from read_config import engine_text 
from csv import writer 
#样本训练
from sklearn.model_selection import train_test_split

"""通过抽查规则 将已经检查过的数据打上是否需要重点检查的标签"""

"""通过生成的关键词处理出只包含一个句子的分类训练样本，形成每个句子的关键词模板，这些模板将作为训练模板
   通过短模板去预测将来遇到的多个句子（拆分开，单个句子做预测）
"""

def compare_range_in_tuple(tuple_a,tuple_b):
	"""
	对比(2,5) (4,5) /(2,4) (2,6)哪个区间范围大
	"""
	#至少保证一个数字相同
	if tuple_a[0] != tuple_b[0] and tuple_a[1] != tuple_b[1]:
		return None 
	if (tuple_a[1]-tuple_a[0]) > (tuple_b[1]- tuple_b[0]):
		return tuple_a
	elif (tuple_a[1]-tuple_a[0]) == (tuple_b[1]- tuple_b[0]):
		return 0 
	else: 
		return tuple_b

#将result_iter排序
def sort_result_iter(result_iter):
	"""
	通过匹配到的概念，根据概念所带的index，对概念进行先后顺序的排序,不考虑段落拆分问题
	:param kme.result_iter
	:return sorted concept and result list
	"""
	result_iter_list = [ ]
	for concept,results in result_iter.items():
		for result in results :
			beg_index_dict = result.get_index('beg_index').to_dict()
			end_index_dict = result.get_index('end_index').to_dict()
			result_iter_list.append((concept,result))

	result_iter_list = sorted(result_iter_list,key=lambda x:x[1].beg_index.offset)
	return result_iter_list

def convert_concepts2sentences(dupliated_deleted_list):
	"""将关键词句子根据句子和段落拆分，加入不同的间隔符号
	:param dupliated_deleted_list : 格式 [(concept, result),...] 
	:return : 返回一个类似正常句子的格式，有逗号，句号(区分段落)"""
	pre_para_counter = 0
	pre_sent_counter = 0 
	i_sent_list = [ ]
	i_para_list = [ ]

	list_length = len(dupliated_deleted_list)
	counter = 0 

	for concept, result in dupliated_deleted_list:
		counter  += 1 
		current_para = result.beg_index.i_para
		current_sent = result.beg_index.i_sent

		if counter == 1 :
			pre_para_counter = current_para
			pre_sent_counter = current_sent

		if current_sent > pre_sent_counter :
			if i_sent_list :
				i_para_list.append(i_sent_list)
			#换段落
			i_sent_list = [ ]
		else:
			i_sent_list.append(concept)

		if counter == list_length and i_sent_list:
			i_para_list.append(i_sent_list)

	join_result = '.'.join([ ' '.join(sent_concepts) for sent_concepts in i_para_list ]) 

	return  join_result 

def concept_drop_overlapping(result_filted_list):
	"""
	:param result_filted_list :区分段落保留的概念列表 [[],[]]
	对经过排序的result_iter_list进行去重，保证区间较长的概念被保留
	如果出现一个概念涵盖另一个概念范围，只选择涵盖范围大的概念记录
	"""
	counter = 0 
	#记录 匹配到的最长概念单词
	all_result_list = [ ]
	record_list = [ ]

	for concept, result in result_filted_list:
		counter +=  1 
		four_element_tuple = (concept, result)
		offset_tuple = (result.beg_index.offset,result.end_index.offset)

		#和上一个概念对比，检查是否应该替换掉上一个概念
		if counter == 1:
			record_list.append(four_element_tuple)
		else:
			pre_record_concept = record_list[-1][0]  
			#取出后面一个元素，对比当前这个
			previous_offset_tuple = (record_list[-1][1].beg_index.offset,record_list[-1][1].end_index.offset) 
			larger_range =  compare_range_in_tuple(offset_tuple,previous_offset_tuple)

			#加上concept != pre_record_concept的条件，删掉连续重复的概念 [and, and,and, people,and] --> [and, people, and]
			if concept != pre_record_concept :
				if larger_range == None :  #如果没有重合部分直接添加进去
					record_list.append(four_element_tuple)
				#如果有重合的地方，并且返回了新的，把之前的元素替换掉,concept不做处理
				elif  offset_tuple == larger_range: 
					record_list[-1] = four_element_tuple
	#加总全部段落概念
	if record_list:
		all_result_list += record_list
	#如果比不上之前的一个元素 offset_tuple != larger_range说明之前的元素有重合并且比这个大,不做处理
	return all_result_list


def sort_filt_drop_select(result_iter):
	"""通过获取的result_iter 进行概念的排序，过滤，丢弃有overlapping的概念
	:return 返回[(concept,result)]
	"""
	sorted_result_list = sort_result_iter(result_iter)
	# 过滤掉目标ECC大类不同段落，超出前后1个句子距离的部分
	# result_filtered_list = filt_concept_target_range(sorted_result_list)
	#去掉重复的概念
	dupliated_deleted_list = concept_drop_overlapping(sorted_result_list)

	return dupliated_deleted_list

pattern_dot = re.compile(' *\.+ *')
pattern_tridot = re.compile(' *\.\.\.+ *')
feff = chr(0xfeff)

def pre_process(line):
	# 逗号有时候会分不开
	line = line.replace(',', ', ')
	# no. 1 这种不应该区分句子
	line = line.replace('no.', 'no ')
	# etc. 变成 etc 不用跨句子
	line = line.replace('etc.', 'etc ')
	line = line.replace('&amp;', ' and ')
	line = line.replace('&#039;', '\'')
	line = line.replace('’', '\'')
	line = line.replace('+', ' + ')
	line = line.replace('°', ' degree ')
	# 多个点 至少3个 变成逗号
	line = pattern_tridot.sub(', ', line)
	# 多个点 变成逗号
	line = pattern_dot.sub('. ', line)
	# * 不要
	line = line.replace('*', ' ')
	# etc. 变成 etc 不用跨句子
	line = line.replace('(', ' ( ')
	line = line.replace(')', ' ) ')
	# 干掉 FEFF
	line = line.replace(feff, ' ')
	
	# 干掉 \r  修改，变成空格，而不是直接去掉
	line = line.replace('\r', ' ')
	line = line.replace("\""," ")
	#修改，加入拆分 \ 符号, 认为之间是存在两个独立单词
	line = line.replace('/',' ')
	line = line.replace('&',' & ')
	#去掉前面的未知空格符，有空格符在EXCEL看不到,关键词在第一的位置无法识别，打印能看到这种空格
	line = line.strip()
	pattern = '[A-Z]?[a-z]+[A-Z0-9]+[a-zA-Z]+' 
	sub_pattern = '[A-Z0-9]+[a-z]+'
	line = split_wrong_combine(pattern,sub_pattern,line)
	return line 

def run(model, line):
	#内容为空不处理
	concept_sentence = ''
	if type(line) == str and line.strip() != '':
		line = pre_process(line)
		#获取到匹配的关键字词组结果
		result_iter = model.match(line)
		#过滤掉不需要的部分
		dupliated_deleted_list = sort_filt_drop_select(result_iter)
		#输入的经过overlapping去重过的概念数据, 转换成普通的句子格式-->有空格，有句号
		concept_sentence = convert_concepts2sentences(dupliated_deleted_list)
	return concept_sentence

def main(model,sql_result,save_path):

	def save(csv_obj,returns_ids,returns_concepts): #超过内存后，将数据以一定的方式存进文件
		for _id, concepts in zip(returns_ids,returns_concepts):
			ret_concepts = concepts.get()
			csv_obj.writerow([_id,ret_concepts])
		print('已保存',round(time.clock(),0))

	write_file = open(save_path,'a+',newline='')
	csv_obj = writer(write_file, dialect='excel')
	#多进程
	pool = Pool(4)
	buff_size = 5000
	returns_ids = [ ]
	returns_concepts = [ ]
	counter = 0 
	return_counter = 0 
	all_results = sql_result.fetchall()
	total_num = len(all_results)
	print('数据总量：',total_num)
	for ret in all_results:
		counter += 1 
		_id = ret[0]
		main_body = ret[1]
		concept_ApplyResult = pool.apply_async(run,args=(model,main_body))

		returns_ids.append(_id)
		returns_concepts.append(concept_ApplyResult)
		if len(returns_ids) > buff_size:
			print('已完成','{}/{}'.format(counter,total_num),round(time.clock(),0))
			save(csv_obj,returns_ids,returns_concepts)
			returns_ids, returns_concepts = [ ],[ ]

	pool.close()
	pool.join()

	#最后一部分
	if returns_concepts :
		print('已完成最后的部分:', counter)
		save(csv_obj,returns_ids, returns_concepts)

	write_file.close()


#从数据库提取评论数据和对应的人工分类结果，生成概念结果，记录到两个字典文件
#原则1：没有出现任何关键词概念的句子就不做保存（分类明显为“无”的句子不放入训练）

if __name__  == '__main__':

	config = {
	'max_text_length': 5000,
	'char_level': False,
	'with_pos': False,
	'language': 'en',
	'force_concept_size_one': False,
	}

	rule_path = 'rules\\c2_rules'

	#生成kme模型
	t1 = time.clock()
	model = train_model(rule_path,config)
	t2 = time.clock()
	print('KME模型已生成,用时：{}秒'.format(round(t2-t1,0)))

	#限定一年数据，只提取有分类的样本, 无分类的样本数量太多，打算另外找时间跑
	sql = """
			select distinct b._id,a.main_body
					from ecommerce_data_original_posts a 
				right join (
						select  _id,comment_time,fault_phen
						from ecommerce_data  
						where enddate >= '20190101'  and enddate < '20200101'
			            and fault_phen = '无'  ) b 
				on a._id = b._id 
				order by b._id; 
	"""

	conn, db = get_sql_connection(engine_text)
	sql_result = conn.execute(sql)
	#保存为CSV格式文件
	save_path = 'concept_training\\id_concepts.csv'
	main(model,sql_result,save_path)
	#关闭
	close_sql_connection(conn,db)
