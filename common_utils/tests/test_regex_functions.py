import sys
sys.path.append("..")

from regex_functions import *
import unittest 

class TestRegexFunctions(unittest.TestCase):

	def test_replace_multi_symbol(self):
		test_string = 'System  respond slowly/not fluent/lagging'
		result = replace_multi_symbol(test_string, ' ')
		self.assertEqual(result,'System respond slowly/not fluent/lagging' )

	def test_strQ2B(self):
		test_string = '。you try try（哈哈）、·》this is not right'
		result = strQ2B(test_string)
		self.assertEqual(result,'.you try try(哈哈)、·>this is not right')

	def test_repalce_re_special(self):
		test_string = 'kerap bertukar rangkaian (2G/3G/4G)'
		result =  replace_re_special(test_string)
		self.assertEqual(result,'kerap bertukar rangkaian \(2G/3G/4G\)')

if __name__ == '__main__':

	unittest.main()

	# text = ',Tingkat sinyal rendah,Fungsi aplikasi tidak normal,aa,'

	# a = re.split('(Tingkat sinyal rendahs|Tingkat sinyal rendah|Fungsi aplikasi tidak normal|aa,eeli)', text,flags=re.I)

	# print(a)
	# exit()