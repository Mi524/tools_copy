import sys
sys.path.append("..")

from os_functions import choose_folder,get_walk_abs_files
import unittest 

class TestCase(unittest.TestCase):


	def test_choose_folder(self):
		self.assertEqual(choose_folder('..\\'),'..\\tests')


	def test_get_walk_abs_files(self):
		#不存在的文件夹
		path = r"D:\My Documents\Documents\vchat\NewChatFiles\Scripts\data_processing_tool\inputs_data\Feedback_test.xlsx"
		result = get_walk_abs_files(path)
		print(result)
		#


if __name__ == '__main__':
	unittest.main()






