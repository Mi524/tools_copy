import win32com.client as client
import argparse
import os 
from common_utils.os_functions import enter_exit, check_create_new_folder, read_from_text
import traceback
import logging

try:
    whatever()
except Exception as e:
    logging.error(traceback.format_exc())


def run_vba(original_path,new_path,macro,macro_sub_name):
	#检查输出文件夹 是否存在
	if not os.path.isfile(original_path):
		enter_exit(f"File not found: {original_path}")

	check_create_new_folder(new_path)
	#打开文档，运行VBA, 如果有报错，everything 搜索gen_py文件 删除，让系统重新生成新的gen_py
	xlapp = client.gencache.EnsureDispatch('Excel.Application')   
	# xlapp = client.dynamic.Dispatch('Excel.Application')
	# xlapp = client.DispatchEx('Excel.Application')
	try:
		xlapp.Visible = 0  
		xlapp.DisplayAlerts = False 
		xlwb = xlapp.Workbooks.Open(original_path,ReadOnly=1) 
		xlwb.Visible = 0
		xlwb.VBProject.VBComponents.Add(1)

		for i in xlwb.VBProject.VBComponents:
			if i.name == '模块1':
				module = xlwb.VBProject.VBComponents.Item(i.name).CodeModule
				module.AddFromString(macro)  
				xlwb.Application.Run(macro_sub_name)

		xlwb.SaveAs(new_path,FileFormat=51,ConflictResolution=2)
		xlwb.Close(True)
	except Exception as e :
		logging.error(traceback.format_exc())
	finally:
		xlapp.Quit
		del xlapp

	print("{} Draw completed".format(new_path.split('\\')[-1]))

if __name__ == "__main__":

	cwd = os.getcwd()

	#参数传入配置文件夹
	parser = argparse.ArgumentParser()
	parser.add_argument('-v',type=str,required=False,
						help = '放VBA的文件夹 vba folder dir', default='VBA')
	parser.add_argument('-i',type=str,required=False,
						help = '输入文件夹 input folder dir', default='input_dir')
	parser.add_argument('-o',type=str,required=False,
						help = '输出文件夹 output folder dir', default='output_dir')

	parser.add_argument('-m',type=str,required=False,
						help = '运行的宏的名称，默认为macroScript', default='macroScript')

	args = parser.parse_args()

	#VBA文本路径
	vba_dir = args.v
	#输入EXCEL文件位置
	input_dir = os.path.join(cwd, args.i)
	#输出文件位置
	output_dir = os.path.join(cwd, args.o)
	#宏的名称
	macro_sub_name = args.m

	vba_files = [ x for x in  os.listdir(vba_dir) if '.txt' in x ]

	for vba in vba_files:
		macro_path = os.path.join(vba_dir,vba)
		input_file = os.path.join(input_dir,vba.replace(".txt",".xlsx"))
		draw_result_file = os.path.join(output_dir,vba.replace(".txt",".xlsx"))

		macro = read_from_text(macro_path)
		try:
		    run_vba(input_file,draw_result_file,macro,macro_sub_name)
		except Exception as e:
		    print(macro_path,input_file,"VBA运行出现问题")
		    print(e)
