import pandas as pd 
import os 
import warnings
import sys 
import re
from xlsxwriter.exceptions import FileCreateError

warnings.filterwarnings('ignore')

base_dir = '.\\'
input_dir = '.\\inputs'
output_dir = '.\\outputs'

file_list = [ x for x in os.listdir(input_dir) if '.xls' in x and '~$' not in x  ]

if file_list:
    file_list = sorted(file_list)
else:
    sys.exit()

#获取关键词需要TOP几的数量
top_num  = input('---TOP排名---： ')

# top_num = ''

if top_num.strip() == '':
    top_num = None
else:
    try: 
        top_num = int(top_num.strip())
    except:
        print('输入的数字有误')
        sys.exit()

#读取本文件夹排序第一的EXCEL
for file in file_list:
    file_path = os.path.join(input_dir,file)

    print('打开文档: ',file_path)
    try:
        original_df = pd.read_excel(file_path ,sheet_name = 'keyword_matched')
    except ValueError:
        print('找不到keyword_matched工作簿')
        exit()

    df = original_df.copy()

    for c in df.columns[1:]:
        df[c] = df[c].apply(lambda x: x.split(',') if type(x) == str else x )
    for c in df.columns[1:]:
        df[c] = df[c].apply(lambda x: len(x) if type(x) == list else 0 )
    df_melt = df.melt(id_vars = 'testid', value_name='数量', var_name='关键词类型' )
    df_melt['数量'] = df_melt['数量'].astype(int)

    #排序
    df_result= df_melt.sort_values(by= ['testid','数量'], ascending= [True,False])

    df_result['排序'] = df_result.groupby(['testid']).cumcount() + 1 

    if top_num != None:
        df_result = df_result.loc[df_result['排序'] <= top_num,: ]
    else:
        #如果不做排名,删除数量未空的
        df_result = df_result.loc[df_result['数量']!=0,:]


    #获取到命中的关键词进行匹配,填在最后一列
    non_split_word_df_melt = original_df.melt(id_vars='testid',value_name='命中关键词', var_name='关键词类型')
    non_split_word_df_melt = non_split_word_df_melt.loc[non_split_word_df_melt['命中关键词'].isna()==False,:]

    df_result = pd.merge(df_result,non_split_word_df_melt,'left',on=['testid','关键词类型'])

    #重新排列表头顺序
    column_list = ['testid','关键词类型','排序','数量','命中关键词']

    df_result =  df_result.loc[:,column_list]

    if top_num == None:
        top_num = ''

    file_name = os.path.split(file_path)[-1]
    result_name =  re.match('(.*).(xlsx|xls|xlsm)$',file_name).group(1) + '_result{}.xlsx'.format(top_num)

    result_name = os.path.join(output_dir, result_name)

    #保存全部文档
    check_close = 0  

    while check_close <= 0:
        try:
            df_result.to_excel(result_name,index=False)
            check_close += 1 
            print(f'结果已保存到{result_name}')
            print('')
        except (PermissionError,FileCreateError) as e :
            input('无法正常记录，请关闭{}后摁回车键继续'.format(result_name))

    
    
