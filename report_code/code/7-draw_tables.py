"""获取写入的文档并调用VBA画图"""
import win32com.client as client
import os 
import datetime 
from dateutil.relativedelta import relativedelta
from pathlib import Path

from common_utils.os_functions import check_create_new_folder,enter_exit
from read_config import engine_text,base_dir,input_dir,output_dir, result_dir, output_draw_dir, startdate, enddate 

def run_vba(original_path,new_path,macro):
	#检查输出文件夹 是否存在
	if not os.path.isfile(original_path):
		enter_exit("File not found: ",original_path)

	check_create_new_folder(new_path)
	#打开文档，运行VBA, 如果有报错，everything 搜索gen_py文件 删除，让系统重新生成新的gen_py
	xlapp = client.gencache.EnsureDispatch('Excel.Application')   
	# xlapp = client.dynamic.Dispatch('Excel.Application')
	# xlapp = client.DispatchEx('Excel.Application')
	xlapp.Visible = 0  
	xlapp.DisplayAlerts = False 
	xlwb = xlapp.Workbooks.Open(original_path,ReadOnly=1) 
	xlwb.Visible = 0
	xlwb.VBProject.VBComponents.Add(1)

	for i in xlwb.VBProject.VBComponents:
		if i.name == '模块1':
			module = xlwb.VBProject.VBComponents.Item(i.name).CodeModule
			module.AddFromString(macro)  
			xlwb.Application.Run("drawNegativeRate")

	xlwb.SaveAs(new_path,FileFormat=51,ConflictResolution=2)
	xlwb.Close(True)
	xlapp.Quit
	del xlapp

	print("{} Draw completed".format(new_path.split('\\')[-1]))

"""获取结果表数据并画图保存文档"""

vba_files = [ x for x in  os.listdir('vba_1.0') if '.txt' in x ]
vba_files = sorted(vba_files,key=lambda x: int(x.split('-',2)[0])) 

for vba in vba_files:
	macro_path = os.path.join('.\\vba_1.0',vba)
	result_file = os.path.join(result_dir,vba.replace(".txt",".xlsx"))
	draw_result_file = os.path.join(output_draw_dir,vba.replace(".txt",".xlsx"))

	with open(macro_path,'r',encoding='utf-8') as file :
		macro =  file.read()
		try:
		    run_vba(result_file,draw_result_file,macro)
		except Exception as e:
		    print(macro_path,result_file,"画图出现问题")
		    print(e)