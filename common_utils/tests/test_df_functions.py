import unittest
import pandas as pd 
from common_utils.df_functions import *
from common_utils.func_classes import * 

class TestCase(unittest.TestCase):

	def test_group_word_sum(self):
		df = pd.DataFrame({ 'a':['t','tt','tt'],
			                'b':[{'aa':2,'cc':3 },{'cc':2,'bb':1}, {'cc':2, 'dd':1}] })

		# result = group_word_sum(df,['a'], 'b')

	# def test_DfDict(self):
	# 	test =  {'a':1,  'b':2, 'c':3}
	# 	test1 = {'a':2,  'b':4       } 
	# 	test2 = {'a':0,  'b':1,       'd': 9}
	# 	test3 = {'a':0,  'b':0,       'd': 0}
	# 	test4 = {'a':-1, 'b':0, 'c': 9}

	# 	df_dict = DfDict(test)
	# 	df_dict1 = DfDict(test1)
	# 	df_dict2 = DfDict(test2)
	# 	df_dict3 = DfDict(test3)
	# 	df_dict4 = DfDict(test4)

	# 	self.assertDictEqual(df_dict + df_dict1, {'a':3,'b':6,'c':3})
	# 	self.assertDictEqual(df_dict + df_dict1 + df_dict2, {'a':3,'b':7,'c':3,'d':9})
	# 	self.assertDictEqual(df_dict - df_dict1 - df_dict2, {'a':-1,'b':-3,'c':3,'d':-9})
	# 	self.assertDictEqual(df_dict * df_dict1 / df_dict2, {"b": 8.0, "c": 0.0, "d": 0.0})
	# 	self.assertDictEqual(df_dict / df_dict1 / df_dict2, {"b": 0.5, "c": 0.0, "d": 0.0})
	# 	self.assertDictEqual(df_dict & df_dict1 & df_dict2, {'a':False,'b':True,'c':False,'d':False})
	# 	self.assertDictEqual(df_dict3 | df_dict4 , {'a':True,'b':False,'c':False,'d':False})
		# self.assertDictEqual(df_dict * df_dict1 - df_dict2, {'a':2,'b':7,'c':0,'d':-9})

	def test_df_query(self):

		test_df = pd.DataFrame({
								'time':['2020-11-11','2020-10-22'],
								'test':[1,3]
								})

		test_df['time'] = pd.to_datetime(test_df['time'])
		result = test_df.query(" time > '2020-11-10' ")
		print(result)

if __name__ == '__main__':
	# test_suite = unittest.TestSuite()
	# test_suite.addTest(TestCase('test_remove_numbers'))
	unittest.main()