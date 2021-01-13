from common_utils.os_functions import get_require_files,get_walk_abs_files,last_day_of_month
from common_utils.sql_functions import write2table,insert_update_table,get_sql_result 
import pandas as pd 
import gc 
import datetime 
import time 
from dateutil.relativedelta import relativedelta 
from read_config import engine_text,base_dir,input_dir,output_dir, startdate, enddate 

base_dir = "..\\原始评论内容"

files = get_walk_abs_files(base_dir)

usecols = ['_id','title','main_body','time']
usecols_2 = ['_id','title','main_body With Macro','time']
usecols_3 = ['_id','comment_time','title','content']

t1 = time.clock()

for f in files :
    print(f)
    df = pd.read_excel(f,sheet_name='content')
    #df = pd.read_csv(f,delimiter=',',quotechar='"',escapechar='\\')
    if 'main_body' in [x.lower() for x in df.columns]:
        df = df.loc[:,usecols]
    elif 'content' in [x.lower() for x in df.columns]:
        df = df.loc[:,usecols_1]
    elif 'comment_time' in [x.lower() for x in df.columns]:
        df = df.loc[:usecols_2]
    else: 
        df = df.loc[:,usecols_3]

    # df = df.rename({'time':'comment_time','main_body With Macro':'main_body'},axis=1)
    # df['enddate'] = df['comment_time'].apply(lambda x : last_day_of_month(x))
    # df = df.loc[(df['enddate']<= enddate)&(df['enddate']>= startdate),:]


    t2 = time.clock() 
    print('用时',t2- t1)

    print('开始写入',len(df),'条记录')

    write2table(engine_text,df,'ecommerce_data_original_posts',how='mysql_load')

    print(f,'已写入')

    t3 = time.clock()
    print('用时',t3 - t2)
