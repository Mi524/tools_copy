import os
import unittest
from common_utils.nlp_functions import * 

class TestCase(unittest.TestCase):

	def test_remove_numbers(self):
		lst = ['aee','34','444']
		self.assertEqual(remove_numbers(lst),['aee'])

if __name__ == '__main__':
	# test_suite = unittest.TestSuite()
	# test_suite.addTest(TestCase('test_remove_numbers'))

	unittest.main()
