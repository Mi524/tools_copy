import sys
sys.path.append("..")

from sequence_functions import *
import unittest 


class TestSequence_Functions(unittest.TestCase):

	def test_duplicate_elem_add_seq(self):
		lst = ['total amount', 'days', 'days', 'weeks', 'weeks']

		result = duplicate_elem_add_seq(lst)
		self.assertEqual(result, ['total amount', 'days', 'days1', 'weeks', 'weeks1'])


if __name__ == '__main__':
	unittest.main()