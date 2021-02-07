from xlrd import open_workbook 
import re 
import os 
import json 
import traceback
import logging
from hanziconv import HanziConv
from common_utils.os_functions import enter_exit

#默认配置,拼接成Html文件代码,网页load data的方	式 不适用于本地文件
js_dir = '.\\config_and_js'
js_pathes = [os.path.join(js_dir,x) for x in os.listdir(js_dir) if x.split('.')[-1]=='js'] 

js_texts = [ ]
for js in js_pathes:
	with open(js,'r',encoding='utf-8') as file:
		js_text = file.read()
		js_texts.append(js_text)

# js_texts = '\t\n'.join(['<script type="text/bjavascript"> ' + x + '</script>' for x in js_texts])
#修改成固定的js文件

with open(os.path.join(js_dir,'echarts_calc_time.min.js'),encoding='utf-8') as file:
	#可以统计点击时间的版本
	js_frame_text = file.read()

with open(os.path.join(js_dir,'echarts_pictures.min.js'),encoding='utf-8') as file:
	js_no_frame_text = file.read()

# with open(os.path.join(js_dir,'echarts_original.min.js'),encoding='utf-8') as file:
# 	js_no_frame_text = file.read()

js_frame_text = '<script type="text/javascript"> ' + js_frame_text + '</script>' 
js_no_frame_text = '<script type="text/javascript"> ' + js_no_frame_text + '</script>' 

#需要将大括号 全部转成 双大括号 才能使用 format()
text_contain_frame = """
<!DOCTYPE html>
<html style="height: 100%"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>
   <body style="height: 100%; margin: 0 0 0 0px">
		<div id="submitpart" style="height: 100%; margin-right:80%; width:300px;float:left; background-color: rgba(50, 50, 50, 0.15)" >
			<div id="submitCheckBox" style="overflow-y:scroll;display:inline-block;background-color: #f8f8f8; height:70%; width:300px; background-color: rgba(50, 50, 50, 0.25)">
			</div>

				<form id='buttonForm1' class='form' style='text-align:center'>
					<button id="checkAllNodes" type="button" style="text-align:center; margin:5% 1% 0 1%; height:30px; width:120px; font-size:15px" onclick="checkAll();return false">Check all</button> 
					<button id="checkAllNodes" type="button" style="text-align:center; margin:5% 1% 0 1%; height:30px; width:120px; font-size:15px" onclick="checkReverse();return false">Inverse</button> 
				</form>

				<form id='buttonForm2' class='form' style='text-align:center'>
					<button id="checkedNodes" type="button" style="text-align:center; margin:5% 1% 0 1%; height:30px; width:120px; font-size:15px" onclick="countChecked();return false">Item Amount</button> 
					<button type="submit" id ="refreshPageId" style="text-align:center; margin:5% 1% 0 1%; height:30px; width:120px; font-size:15px" onclick="refreshPage();return true">Refresh Page</button> 
				</form>

				<form id='buttonForm3' class='form' style='text-align:center'>
					<button id="copySelectedId" type="button" style="text-align:center; margin:5% 1% 0 1%; height:30px; width:120px; font-size:15px" onclick="copySelected();return false">Copy Selected</button> 
				</form>
				
				<div style="text-align: center">
					 <input type="text" style="margin:6% 0 0 0; width:140px; height:20px; font-size:15px; text-align:center" id="timetext" value="Timer: 0H 0M 0S" readonly><br>
					 <!--button type="button" style="margin:2% 0 0 0; font-size:15px" onclick="startTimer()">Start</button--> 
					 <!--button type="button" style="margin:2% 0 0 0; font-size:15px" onclick="stopTimer()">Pause</button--> 
					 <!--button type="button" style="margin:2% 0 0 0; font-size:15px" onclick="resetTimer()">Reset</button-->
				</div>
		</div>
  
	   <div id="container" style="height: 100%; margin-left:20%; margin-bottom:0%; margin-top:0%; -webkit-tap-highlight-color: transparent; user-select: all; position: relative;" _echarts_instance_="ec_1591200401189">
			<div style="position: relative; width: 1280px; height: 667px; padding: 0px; margin: 0px; border-width: 0px; cursor: default;">
				<canvas data-zr-dom-id="zr_0" width="2560" height="1334" style="position: absolute; left: 0px; top: 0px; width: 1280px; height: 667px; user-select: none; -webkit-tap-highlight-color: rgba(0, 0, 0, 0); padding: 0px; margin: 0px; border-width: 0px;">
				</canvas>
				<div style="position: absolute !important; visibility: hidden !important; padding: 0px !important; margin: 0px !important; border-width: 0px !important; user-select: none !important; width: 0px !important; height: 0px !important; left: 0px !important; top: 0px !important; right: auto !important; bottom: auto !important;">
				</div>
				<div style="position: absolute !important; visibility: hidden !important; padding: 0px !important; margin: 0px !important; border-width: 0px !important; user-select: none !important; width: 0px !important; height: 0px !important; right: 0px !important; top: 0px !important; left: auto !important; bottom: auto !important;">
				</div>
				<div style="position: absolute !important; visibility: hidden !important; padding: 0px !important; margin: 0px !important; border-width: 0px !important; user-select: none !important; width: 0px !important; height: 0px !important; left: 0px !important; bottom: 0px !important; right: auto !important; top: auto !important;">
				</div>
				<div style="position: absolute !important; visibility: hidden !important; padding: 0px !important; margin: 0px !important; border-width: 0px !important; user-select: all !important; width: 0px !important; height: 0px !important; right: 0px !important; bottom: 0px !important; left: auto !important; top: auto !important;">
				</div>
			</div>    
			<div style="position: absolute; display: none; border-style: solid; white-space: nowrap; z-index: 9999999; transition: left 0.4s cubic-bezier(0.23, 1, 0.32, 1) 0s, top 0.4s cubic-bezier(0.23, 1, 0.32, 1) 0s; background-color: rgba(50, 50, 50, 0.7); border-width: 0px; border-color: rgb(51, 51, 51); border-radius: 4px; color: rgb(255, 255, 255); font: 14px / 21px sans-serif; padding: 5px; left: 484px; top: 353px; pointer-events: none;">格式1.手机品质类
			</div>
	   </div>

	   <script>
			function countChecked() {{
				var submitCheckBox = document.getElementById("submitCheckBox");
				var submitNodes = submitCheckBox.childNodes;
				var checkedNum = 0 ; 
				for (i=0; i < submitNodes.length; i++){{
					var child = submitNodes[i];
					if (child.class === "checks" && child.checked === true){{
						checkedNum = checkedNum + 1
					}}
				}}
				checkedNodes = document.getElementById("checkedNodes");
				checkedNodes.innerHTML = 'Checked: ' + checkedNum;
				return checkedNum
			}}
			function refreshPage() {{
				//预留
			}}
			function refreshList() {{ //预留函数，未能配合实现单纯地刷新列表
				var submitCheckBox = document.getElementById("submitCheckBox");       
				submitCheckBox.innerHTML = '';
				//清空列表后，需要把js里面的树图记录的东西也清空 this.checkedNodes
			}}
			function checkAll(){{
				var submitCheckBox = document.getElementById("submitCheckBox");
				var submitNodes = submitCheckBox.childNodes;

				for (i=0; i < submitNodes.length; i++){{
					var child = submitNodes[i];
					if (child.class === "checks" && child.checked === false){{
						child.checked = true
					}}
				}}
			}}
			function checkReverse(){{
				var submitCheckBox = document.getElementById("submitCheckBox");
				var submitNodes = submitCheckBox.childNodes;

				for (i=0; i < submitNodes.length; i++){{
					var child = submitNodes[i];
					if (child.class === "checks" && child.checked === false){{
						child.checked = true
					}} else if (child.class === "checks" && child.checked === true){{
						child.checked = false
					}}
				}}
			}}
			function copyStringToClipboard (str) {{
			   var el = document.createElement('textarea');
			   el.value = str;
			   el.setAttribute('readonly', '');
			   el.style = {{position: 'absolute', left: '-9999px'}};
			   document.body.appendChild(el);
			   el.select();
			   document.execCommand('copy');
			   document.body.removeChild(el);
			}}
			function copySelected() {{
				var submitCheckBox = document.getElementById("submitCheckBox"),
					submitNodes = submitCheckBox.childNodes,
					selectedTextList = [],
					btnCopy = document.getElementById("copySelectedId"),
					selectedText = "";
				for (i=0; i < submitNodes.length; i++){{
					var child = submitNodes[i];
					
					if (child.class === "checks" && child.checked === true){{
						selectedTextList.push(child.value);
					}} 
				}}
				selectedText = selectedTextList.join("\\n");
				if (selectedText !== ""){{
					copyStringToClipboard(selectedText);
					alert("Items are copied")
				}}
			}}
			var hour,minute,second;//时 分 秒
			hour=minute=second=0;//初始化
			var int;
			//重置
			function resetTimer() {{
			   window.clearInterval(int);
			   hour=minute=second=0;
			   document.getElementById('timetext').value='Timer: 0H 0M 0S'
			}}

			function startTimer() {{
				window.clearInterval(int);
				int=setInterval(timer,1000);
			}}

			function timer()
			{{
			   second = second + 1;
				if (second >= 60) {{
					second = 0;
					minute = minute + 1;
				}}
				if ( minute >= 60 ) {{
					minute = 0;
					hour = hour + 1;
				}}
			document.getElementById('timetext').value='Timer: ' + hour+'H '+minute+'M '+second+'S';
			}}

			function stopTimer() {{
				window.clearInterval(int);
			}}
	   </script>  

	   {}
	   <script type="text/javascript">

		var dom = document.getElementById("container");
		var myChart = echarts.init(dom);
		var app = {{}};
		option = null;
""".format(js_frame_text)


text_no_frame =  """
<!DOCTYPE html>
<html style="height: 100%">
   <head>
	   <meta charset="utf-8">
   </head>
   <body style="height: 100%; margin: 0">
	   <div id="container" style="height: 100%"></div>
	   {}
	   <script type="text/javascript">
var dom = document.getElementById("container");
var myChart = echarts.init(dom);
var app = {{}};
option = null;
""".format(js_no_frame_text)


text_2 = """
		var option = {
			tooltip: {
				trigger: 'item',
				triggerOn: 'mousemove'
			},
			series:[
				{
					type: 'tree',
					id: 0,
					name: 'tree1',
					data: [data],

					top: '5%',
					left: '15%',
					bottom: '5%',
					right: '20%',
					
					symbol : 'emptyCircle',
					symbolSize: 12,

					edgeShape: 'curve',
					edgeForkPosition: '60%',
					initialTreeDepth: 1,

					itemStyle:{

						borderColor:'rgb(0, 112, 192)'
					},
					lineStyle: {
						width: 2,
						color : 'rgb(0, 112, 192)',
						curveness : '0.5'
					},

					label: {
						fontSize :15,
						color : 'rgb(0, 0, 0 )',
						labelsize : 20,
						backgroundColor: '#fff',
						position: 'left',

						verticalAlign: 'middle',
						align: 'right'
					},

					leaves: {
						label: {
							position: 'right',
							verticalAlign: 'middle',
							align: 'left'
						}
					},

					expandAndCollapse: true,
					animationDuration: 200,
					animationDurationUpdate: 500
				}
			]
		};;
		if (option && typeof option === "object") {
			myChart.setOption(option, true);
		}
			   </script>
		   </body>
		</html>
"""

#默认没有左边选择框
text_1 = text_contain_frame.strip()
text_2 = text_2.rstrip()

#如果存在配置文件
tree_config_path = 'config_and_js\\config.txt'
if_frame_path = 'config_and_js\\selection_frame.txt'

if os.path.exists(tree_config_path):
	with open(tree_config_path,'r',encoding='utf-8') as file:
		tree_config_text = file.read()
		text_2 = """ var option = {
					  tooltip: {
						trigger: 'item',
						triggerOn: 'mousemove'
					},
				""" + '\n' + tree_config_text + '\n' + \
				"""
				};; if (option && typeof option === "object") {
					myChart.setOption(option, true);
				}
					   </script>
				   </body>
				</html>
			   """
else:
	print("缺少配置文件config.txt")


if_convert_to_tw = False
#如果存在是否有左边选项框的配置
if os.path.exists(if_frame_path):
	with open (if_frame_path,'r',encoding='utf-8') as file:
		if_frame =  file.readlines()
		for x in if_frame:
			x_list = [y.strip() for y in x.split('=')]
			if len(x_list) == 2 and x_list[0] == 'if_contains_selection_frame' :
				if_frame_text = x_list[1]
				if if_frame_text.lower() == 'no':
					text_1 = text_no_frame
			if len(x_list) == 2 and 'if_convert_to_tw' in x_list[0].lower():
				if x_list[1].lower().strip() == 'yes':
					if_convert_to_tw = True 


# 通用转换数组函数
def convert2values(ws):
	ws_values = [ ]
	#由第一行表头确定读取多少列
	header_len = len([x.value for x in ws.row(0) if x.value !=''])
	for row_index in range(1,ws.nrows):
		row_values = [str(x.value).strip() if type(x) == str else x.value for x in ws.row(row_index)[:header_len]  ]
		ws_values.append(row_values)
	return ws_values

def convert2tw(ws_values):
	ws_values_list = [[ HanziConv.toTraditional(x) if type(x) == str else x for x in y ] for y in ws_values ]
	return ws_values_list

#通用函数
def add_empty_children_value(dictionary):
	if dictionary["children"] :
		for child_dict in dictionary["children"]:
			add_empty_children_value(child_dict)
	else:
		dictionary.pop("children")
		dictionary.update({"value":0})
	return dictionary

#以下画普通表格的方式(层级从左到右)
"""
1.将表格数据转成2D list
2.每一行前面有空的意味他的父级在上面的合并单元格中，需要往下填充,但注意后半部分不能填充，即pandas ffill逻辑不适用
(例如：['','','第三级类别A','第四级类别B'])
3.将填充后的列表通过递归方式提取出nested dictionary
4.将nested_dict转换成列表数据格式[{'name':xx,'children':[ xx..... ]}]
5.空的children列表代表后面没有子节点，可以删除
"""

def uneven_list_dictify(values):
	#为了让最后一级也全都是键值
	values = [ x+ [''] for x in values ]
	d = {}
	for row in values:
		here = d
		for elem in row[:-2]:
			if elem not in here:
				here[elem] = {}
			here = here[elem]
		here[row[-2]] = row[-1]
	return d


def forward_fill(values):
	#区别于pandas的forwordfill,不会填充后面为空的部分，只向前填充前面列空的部分
	complete_row = values[0]
	result = [complete_row]
	#第一行必定是有完整的前几列数据,从第二行开始读取填充
	for v_index in range(1,len(values)):
		value = values[v_index] 
		for i in range(len(value)):
			#如果发现有缺失的部分
			if value[i] == '':
				value[i] = complete_row[i]
			else:
				complete_row = value
				break
		result.append(value)
	return result

def recrusive_dict2list(nested_dict,superior):
	result_dict = {'name':superior,'children':[ ]}
	if type(nested_dict) == dict :
		for k,v in nested_dict.items():
			if k != '':
				temp = recrusive_dict2list(v,k)
				result_dict['children'].append(temp)   

	return result_dict

#普通层级格式的函数整合
def create_common_tree(ws_values,result_dict,zero_level_name):
	values = uneven_list_dictify(ws_values)
	result_dict = recrusive_dict2list(values,zero_level_name)
	result_dict = add_empty_children_value(result_dict)
	return result_dict 

"""
只有一列父节点和子节点两列的层级数据, hirarchy结尾
"""
def find_dict_hirarchy(dictionary,superior,current_value,zero_level_name):
	if superior.strip() == '':
		superior = zero_level_name

	if superior == dictionary["name"]:
		temp_dict = {"name":current_value,"children":[]}
		dictionary["children"].append(temp_dict)
	else :
		for child_dict in dictionary["children"]:
			find_dict_hirarchy(child_dict,superior,current_value,zero_level_name)
	return dictionary

def create_tree_hirarchy(ws_values,result_dict):
	result_dict = {'name':zero_level_name,'children':[ ]}
	#循环第一列，找第二列的父节点 
	for value in ws_values:
		current_value = value[1]
		superior = value[2]
		#如果有上一层，就往上一层的字典添加children节点
		result_dict = find_dict_hirarchy(result_dict,superior,current_value,zero_level_name)
	result_dict = add_empty_children_value(result_dict)
	return result_dict

#开始
if __name__ == '__main__':

	input_dir = '.\\input_dir'
	path_list = [ x for x in os.listdir(input_dir) if '~$' not in x and '.xlsx' in x ]

	if not path_list:
		enter_exit('input_dir没有找到任何Excel文档')
	else:
		for path_original in path_list:
			zero_level_name = path_original.replace('.xlsx','')
			path = os.path.join(input_dir,path_original)

			workbook = open_workbook(path)
			ws = workbook.sheet_by_index(0)

			try:
				#可以共同去掉第一行数据,但只有第二种情况需要fill_empty
				ws_values = convert2values(ws)
				if if_convert_to_tw :
					ws_values = convert2tw(ws_values)

				result_dict = {'name':zero_level_name,'children':[ ]}
					#如果第一行带有Superior Category字样，采用第二种处理方式
				if len(ws.row(0)) <= 2 or str(ws.row(0)[2].value).strip() != 'Superior Category':
					#填充合并单元格造成的空值
					ws_values = forward_fill(ws_values)
					result_dict = create_common_tree(ws_values,result_dict,zero_level_name)   
				else:
					result_dict = create_tree_hirarchy(ws_values,result_dict)

				#修改第0级的节点名称为空，节省空间
				result_dict['name'] = "Category"
				json_object = json.dumps(result_dict,ensure_ascii=False,indent = 4)
				data_text =  'var data = {0}'.format(json_object)

				#写入html文档,将json格式数据替换到html代码文件
				data_pat = 'var data = \{(.*)\}'
				with open(f'{zero_level_name}.html','w',encoding='utf-8') as file :
					file.write(text_1+'\n' + data_text + '\n' + text_2)
				#写入json文档
				# with open('tree.json','w',encoding='utf-8') as file :
				#     file.write(json_object)
				print(f'{path}树图已生成')
			except Exception as e:
				logging.error(traceback.format_exc())
				print(f'*****{path}画图出错*****')
				continue

	# enter_exit('')
