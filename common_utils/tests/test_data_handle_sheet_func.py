import sys 
sys.path.append('..')

from data_handle_sheet_func import * 
import unittest

import pandas as pd 
import sqlite3 

class TestCase(unittest.TestCase):

	def test_exec_write_to_db(self):

		data_df = pd.DataFrame(data_df)
		
		# conn = sqlite3.connect(":memory:")
		conn = sqlite3.connect(r"C:\Program Files\DB Browser for SQLite\test_db.db")


		write_db_config = {'in':[0,1,2],
						   'path':['',
						   			r"D:\My Documents\Documents\vchat\NewChatFiles\Scripts\data_handler\input_data", 
									r"D:\My Documents\Documents\vchat\NewChatFiles\Scripts\data_handler\input_data\calc_amount(India) - day calculations-2021.01.15-2021.01.17.xlsx"],
						   'sheet':['','',''],
						   'table_name':['temp', 'temp1', 'temp2'] }

		write_db_config = pd.DataFrame(write_db_config)

		exec_write_to_db(conn, data_df, write_db_config)

		cursor = conn.cursor()
		cursor.execute("select * from temp ;")
		result = cursor.fetchall()
		conn.close()

		print(result)

if __name__ == '__main__':
	unittest.main()


