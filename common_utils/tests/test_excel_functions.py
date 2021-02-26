from common_utils.excel_functions import refresh_excel_calculations1, \
					refresh_excel_calculations2, refresh_excel_calculations3
import unittest 


class TestCase(unittest.TestCase):

	def test_refresh_excel_calculations2(self):
		path = r"D:\My Documents\Documents\vchat\NewChatFiles\Scripts\data_handler\config_calc_amount(India) - OSversion\1-statistic_config-warning 1.xlsx"
		refresh_excel_calculations2(path)

	def test_refresh_excel_calculations3(self)
		path = r"D:\My Documents\Documents\vchat\NewChatFiles\Scripts\data_handler\config_calc_amount(India) - OSversion\1-statistic_config-warning 1.xlsx"
		
if __name__ == '__main__':
	unittest.main()