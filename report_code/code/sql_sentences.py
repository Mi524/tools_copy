"""提取数据相关的SQL"""
def overall_sources(startdate,enddate):

	sql = f"""
			select source_name 来源,
				   enddate 日期, 
				   fault_type 故障类别,
				   fault_type_num 故障类别数量
				   from overall
			where enddate between '{startdate}' and '{enddate}'
			order by source_name,enddate,
		    case when fault_type_rank <= 6 then  1
				 else fault_type_rank  end , 
		    fault_type_num desc 
	"""
	return sql 

def overall(startdate,enddate):
	sql = """select source_name 来源,
				enddate 日期,
				fault_type_num 故障类别数量,
		  		shipment_half_year 半年销量,
		  		negative_rate 负向口碑占比
		  from result_overall 
		  where enddate between last_day(date_sub('{0}',interval 11 month)) and '{0}'
		  order by enddate;""".format(enddate)

	return sql 


def overall_top6(startdate,enddate):
	sql = """
			select source_name 来源,
				   enddate 日期,
				   fault_type_rank 类别排名,
			       fault_type_report 故障类别, 
			       fault_type_num 故障类别数量,
			       shipment_half_year 半年销量,
			       negative_rate 负向口碑占比
				from result_overall_top6 
				where enddate between last_day(date_sub('{0}',interval 11 month)) and '{0}'
				and fault_type_rank <= 6 
				order by source_name,enddate ; 
			""".format(enddate)

	return sql 


def overall_stability(startdate,enddate):
	sql = """
			select source_name 来源,
				   enddate 日期,
				   fault_type_rank 类别排名,
			       fault_type 故障类别, 
			       fault_type_num 故障类别数量,
			       shipment_half_year 半年销量,
			       negative_rate 负向口碑占比
				from result_overall_original_type 
				where enddate between last_day(date_sub('{0}',interval 11 month)) and '{0}'
				and fault_type_report = '系统稳定性' 
				order by source_name,enddate ; 
			""".format(enddate)

	return sql 


def compare_model():
	"""包括OV和所有竞品机型对比"""
	sql = f"""
	    select brand 品牌,
	    	   series 系列,
	    	   model 机型,
	    	   concat('实销',market_month,'个月') 实销月数,
	    	   fault_type_num_cum 累计故障类别数量,
	    	   comment_num_cum 累计发帖数量 ,
	    	   negative_rate_cum 累计负向口碑占比
	    	   from result_model_market_month ; 
		"""
	return sql 

def compare_model_top(partial_sql,startdate,enddate):
	"""实销日计算TOP故障"""
	sql_1 = f"""
			set @min_date =( select min(max_date) from 
						   ( select brand,model, max(market_day) max_date 
								from com_market_day_comment
								where ( {partial_sql} )
								group by  brand,model )  min_date_table  )  ; 
			"""

	sql_2 = f"""
				select b.brand 品牌,
					   b.series 系列,
					   b.model 机型,
					   @min_date 实销天数, 
					   a.fault_type_report 故障类别, 
					   fault_type_num 故障类别数量,
					   comment_num  发帖数量,
					   fault_type_num/comment_num 负向口碑占比 
					   from 
					   (  select  brand,series, model,
								  case when fault_type_rank <= 6 then 1 
									   else fault_type_rank end fault_type_rank , 
								  fault_type_report, 
								  sum(fault_type_num) fault_type_num
							from com_market_day  
							where  ( {partial_sql} )
							and market_day <= @min_date 
							group by brand,series, model,fault_type_report
							)  a
						   right join 
							(  select   brand,series, model,
										sum(comment_num) comment_num  
									from com_market_day_comment 
									where  ( {partial_sql} )
									and market_day <= @min_date 
									group by brand,series, model
									) b 
						on a.brand = b.brand 
						and a.series = b.series 
						and a.model = b.model 
					order by b.brand,b.model,fault_type_rank, fault_type_num/comment_num desc ;  
			"""

	return sql_1,sql_2


def compare_series(partial_sql,startdate,enddate):

	sql = f"""
				select brand 品牌,
					   series 系列,enddate 日期,
					   fault_type_num 故障类别数量,
					   comment_num 发帖数量, 
					   negative_rate 负向口碑占比 
				   from result_com_series 
				 where enddate >= '{startdate}' and enddate <= '{enddate}'
				 and ( {partial_sql} )
				 order by brand,series,enddate;
	"""
	return sql 

def compare_series_half_year(partial_sql,startdate,enddate):

	sql_1 = f"""
				select 
				brand 品牌,
				series 系列,
				fault_type_report 故障类别, 
				fault_type_num 故障类别数量,
				comment_num 发帖数量,
				negative_rate 负向口碑占比 from 
				result_com_series_half_year
				where enddate = '{enddate}'
				and ( {partial_sql} )
				order by brand, series, case when fault_type_rank <= 6 then 1 else fault_type_rank end, negative_rate desc;
				"""
	#加一个逻辑，半年故障类别差异的对比 
	sql_2 = f"""
			select 
				enddate 月份,
				brand 品牌,
				series 系列,
				fault_type_report 故障类别, 
				fault_type_num 故障类别数量,
				comment_num 发帖数量,
				negative_rate 负向口碑占比 from 
				result_com_series_half_year
				where enddate between date_sub('{enddate}',interval 11 month) and '{enddate}'
				and ( {partial_sql} )
				order by brand, series, case when fault_type_rank <= 6 then 1 else fault_type_rank end, negative_rate desc;
	"""
	return (sql_1,sql_2)


def compare_model_types_market_month():
	"""这里的startdate和enddate没有作用"""
	sql = f"""
			select brand 品牌,series 系列, model 机型, concat('实销',market_month,'个月') 实销月数,
			fault_type_rank 故障类别排名, fault_type_report 故障类别,
			fault_type_num_cum 累计故障类别数量, comment_num_cum 累计发帖数量, 
			negative_rate_cum 累计负向口碑占比 
			from temp_model_market_month_types
	"""

	return sql 


def compare_model_types_nature_month():
	sql = f"""
	    select brand 品牌, series 系列, model 机型, enddate 月份,
	    fault_type_rank 故障类别排名, fault_type_report 故障类别, 
	    fault_type_num 故障类别数量,comment_num  发帖数量, negative_rate 负向口碑占比 
		from temp_model_nature_month_types ; 
	"""
	return sql 

def compare_brand_price(startdate,enddate):
	sql =f"""
			select brand 品牌, 
				   enddate 月份,
			       price_rank 价格排名,
			       price_range 价格区间, 
			       fault_type_num 故障类别数量,
			       comment_num 发帖数量,
			       negative_rate 负向口碑占比 
			   from result_com_price 
			   where enddate between '{startdate}' and '{enddate}' ; 
		"""

	return sql 

def compare_brand_price_types(startdate,enddate):
	sql  =  f"""
			select brand 品牌, 
				   enddate 月份,
			       price_rank 价格排名,
			       price_range 价格区间, 
			       fault_type_rank 故障类别排名,
			       fault_type_report 故障类别 ,
			       fault_type_num 故障类别数量,
			       comment_num 发帖数量,
			       negative_rate 负向口碑占比 
			   from result_com_price_types  
			   where enddate between '{startdate}' and '{enddate}'
			   and fault_type_rank <= 6; 
	"""
	return sql


def get_series_model_contains(startdate,enddate):

	sql_1 = f"""
				select xx.brand  品牌, xx.price_range 价格区间, 
					yy.series_group 系列组合, concat(yy.series_group,'系列') 系列组合_中文 , yy.model_group 机型组合 from 
				(   select brand , price_range from basic_all_brands x  
						inner join basic_price_ranges y 
						on 1 =1 ) xx 
				left join 
				(
					select brand, price_range, 
						   group_concat(distinct series order by length(series),series SEPARATOR  '/')  series_group,
			               group_concat(distinct  model order by launch_date, length(model), model SEPARATOR  '/') model_group
					from
					(select distinct brand, price_range, 
			        replace(series,' Series','') series, replace(series,' Series','系列') series_extra,
			           case when launch_date between last_day(date_sub('{enddate}',interval 1 month)) and '{enddate}' 
					   then concat(model,date_format(launch_date,'(上市日期:%Y/%m/%d)')) 
					   else model end model , 
			           launch_date 
					   from  com_comment_num 
					   where enddate between '{startdate}' and '{enddate}'
					   order by brand,price_range )  a  
					   group by brand, price_range  ) yy 
					on xx.brand = yy.brand and xx.price_range = yy.price_range 
			        order by  xx.price_range, case when xx.brand ='vivo' then 1 else 2 end, xx.brand; 
	"""

	sql_2 = f"""
			select brand 品牌,series 系列, 
				group_concat(model order by launch_date,length(model), model SEPARATOR  '/')  机型组合
				from
				(select  brand, launch_date, replace(series,' Series','系列') series, 
				   case when launch_date between last_day(date_sub('{enddate}',interval 1 month)) and '{enddate}' 
				   then concat(model,date_format(launch_date,'(上市日期:%Y/%m/%d)')) 
				   else model end model, 
				   sum(comment_num) comment_num 
				   from  com_comment_num  
				   where enddate between '{startdate}' and '{enddate}' 
				   and series is not null 
				   group by brand,series,model )  a  
				   group by brand, series
				   order by brand, series  ; 
	"""

	return (sql_1,sql_2)

def ana_overall_month_change(startdate,enddate):
	sql = f"""
		select date_format(本月,'%Y年%m月') 本月, date_format(上月,'%Y年%m月') 上月, 
			来源, 故障类别, 本月单故障数量, 上月单故障数量, 本月故障数量, 上月故障数量,
			本月半年销量, 上月半年销量, 本月单故障反馈率, 上月单故障反馈率, 单故障反馈率变化, 
			本月负向反馈率, 上月负向反馈率, 负向反馈率变化, 变动影响比重
        from temp_ana_overall_types
		where 本月 = '{enddate}';  """
	return sql 

#分析数据
def ana_all_com_phens(startdate,enddate):
	sql = f"""
			select 
			b.price_range 价格区间,
			b.comment_month 月份,
			b.brand 品牌,
			b.series 系列,
			b.model 机型,
			fault_type_report 故障类别_1,
			fault_type 故障类别_2 , 
			fault_phen 故障现象,
			fault_type_num 故障现象数量,
			comment_num 发帖数量,
			round(fault_type_num/ comment_num,4) 负向口碑占比 
			from com_all_phens a
			right join 
			com_comment_num b 
			on a.brand = b.brand 
			and a.series = b.series 
			and a.model = b.model  
			and a.enddate = b.enddate 
			where b.enddate >= last_day(date_sub('{enddate}',interval 5 month)) 
			order by b.enddate desc,b.brand,b.series,b.model,fault_type_report,fault_phen ; 
	"""
	return sql 

def ana_half_year_phens(startdate,enddate):

	sql = f"""
			select 
			comment_month 月份, 
			date_format(startdate,'%Y年%m月') 开始月份, 
			date_format(enddate,'%Y年%m月')  截止月份, 
			brand 品牌, 
			series 系列, 
			model 机型, 
			fault_type_report 故障类别_1, 
			fault_type 故障类别_2, 
			fault_phen 故障现象, 
			fault_type_num 故障类别数量, 
			comment_num 发帖数量, 
			negative_rate 负向口碑占比
			from temp_ana_series_half_year_phens 
			where enddate = '{enddate}' ; 
	"""
	return sql 


def ana_market_month_phens(startdate,enddate):

	sql = """
		select 
			date_format(enddate,'%Y年%m月') 月份,
			brand 品牌, 
			series 系列, 
			model 机型,
			concat('实销',market_month,'个月') 实销月数, 
			 fault_type_report 故障类别_1, 
			 fault_type 故障类别_2, 
			 fault_phen 故障现象, 
			fault_type_num 故障现象数量, 
			comment_num 发帖数量,  
			negative_rate 负向口碑占比
			from temp_ana_market_month_phens 
			order by brand,series, model, market_month,fault_type_report ; 
	"""
	return sql 

# 分析表
def ana_series_month_change(startdate,enddate):
	sql_1 = f"""
		select 
			date_format(本月,'%Y年%m月') 本月,date_format(上月,'%Y年%m月') 上月, 
			品牌, 系列, 机型, 本月机型故障数量, 上月机型故障数量, 
			本月机型发帖数量, 上月机型发帖数量, 本月系列故障数量, 上月系列故障数量, 
			本月系列发帖数量, 上月系列发帖数量, 本月机型负向口碑, 上月机型负向口碑,
			机型负向口碑变化, 上月系列负向口碑, 本月系列负向口碑, 系列负向口碑变化, 
			本月机型故障占比, 上月机型故障占比, 变动影响, 变动影响比重
		from temp_ana_series_month_change_model 
		where 本月 = '{enddate}'
		order by 本月 desc, 品牌, 系列, 变动影响 desc;
	"""

	sql_2 = f"""
		select 
			date_format(本月,'%Y年%m月') 本月,date_format(上月,'%Y年%m月') 上月, 
			品牌, 系列, 故障类别, 
			本月机型故障数量, 上月机型故障数量, 本月机型发帖数量, 上月机型发帖数量, 
			本月系列故障数量, 上月系列故障数量, 本月系列发帖数量, 上月系列发帖数量, 
			本月机型负向口碑, 上月机型负向口碑, 机型负向口碑变化, 上月系列负向口碑, 
			本月系列负向口碑, 系列负向口碑变化, 本月机型故障占比, 上月机型故障占比,
			 变动影响, 变动影响比重
		 from temp_ana_series_month_change_types
		 where 本月 = '{enddate}'
		 order by 本月 desc, 品牌, 系列, 变动影响 desc ;
	"""

	sql_3 = f"""
	 	select 
	 	date_format(本月,'%Y年%m月') 本月,date_format(上月,'%Y年%m月') 上月, 
		品牌, 系列, 机型, 故障类别, 本月机型故障数量, 
		上月机型故障数量, 本月机型发帖数量, 上月机型发帖数量, 本月系列故障数量, 上月系列故障数量, 
		本月系列发帖数量, 上月系列发帖数量, 本月机型负向口碑, 上月机型负向口碑, 机型负向口碑变化, 
		本月系列负向口碑, 上月系列负向口碑, 系列负向口碑变化, 本月机型故障占比, 上月机型故障占比,
		变动影响, 变动影响比重
	 from temp_ana_series_month_change_model_types 
	 where 本月 = '{enddate}'
	 order by 本月 desc, 品牌, 系列, 变动影响 desc ;
	"""

	return (sql_1,sql_2,sql_3)


def ana_price_month_change(startdate,enddate):
	sql_1 = f"""
		select 
			date_format(本月,'%Y年%m月') 本月,date_format(上月,'%Y年%m月') 上月, 
			品牌, 价格区间, 机型, 
			本月机型故障数量, 上月机型故障数量, 本月机型发帖数量, 上月机型发帖数量, 
			本月价位故障数量, 上月价位故障数量, 本月价位发帖数量, 上月价位发帖数量, 
			本月机型故障占比, 上月机型故障占比, 本月机型负向口碑, 上月机型负向口碑, 
			机型负向口碑变化, 本月价位负向口碑, 上月价位负向口碑, 价位负向口碑变化,
			变动影响, 变动影响比重
		from temp_ana_price_month_change_model 
	    where 本月 = '{enddate}' 
	    order by 本月 desc,价格区间, 品牌, 变动影响 desc ;
	"""

	sql_2 = f"""
		select 
			date_format(本月,'%Y年%m月') 本月,date_format(上月,'%Y年%m月') 上月, 
			品牌, 价格区间, 故障类别, 
			本月机型故障数量, 上月机型故障数量, 本月机型发帖数量, 上月机型发帖数量, 
			本月价位故障数量, 上月价位故障数量, 本月价位发帖数量, 上月价位发帖数量, 
			本月类别负向口碑, 上月类别负向口碑, 类别负向口碑变化, 
			上月价位负向口碑, 本月价位负向口碑, 价位负向口碑变化, 
			变动影响, 变动影响比重
		from temp_ana_price_month_change_types
		where 本月 = '{enddate}'
		order by 本月 desc,价格区间, 品牌 , 变动影响 desc ;
	"""

	sql_3 = f"""
	 	select 
	 	date_format(本月,'%Y年%m月') 本月,date_format(上月,'%Y年%m月') 上月, 
		品牌, 价格区间, 机型, 故障类别, 本月机型故障数量, 上月机型故障数量, 本月机型发帖数量, 
		上月机型发帖数量, 本月价位故障数量, 上月价位故障数量, 本月价位发帖数量, 上月价位发帖数量, 
		本月机型负向口碑, 上月机型负向口碑, 机型负向口碑变化, 上月价位负向口碑, 本月价位负向口碑, 
		价位负向口碑变化, 本月机型故障占比, 上月机型故障占比, 
		变动影响, 变动影响比重
	 	from temp_ana_price_month_change_model_types 
	 	where 本月 = '{enddate}'
	 	order by 本月 desc,价格区间, 品牌, 变动影响 desc ;
	"""

	return (sql_1,sql_2,sql_3)


def ana_series_half_year_change(startdate,enddate): 

	#这个已经在临时表写好只提取1个月份的半年
	sql = f"""
		select * from temp_ana_series_half_year  ;   
	"""
	return sql 


def ana_model_market_month_change(startdate,enddate):

	sql = f"""
		select * from temp_ana_model_market_month_change ;   
	"""

	return sql


def ana_model_abnormal_change(startdate,enddate):
	sql_1 = """
	   select  date_format(本月,'%Y年%m月') 本月,
			   date_format(上月,'%Y年%m月') 上月, 
			   变动情况,
			   品牌, 系列, 机型,
			   本月机型故障数量, 
			   本月机型发帖数量,
			   上月机型故障数量, 
			   上月机型发帖数量 ,
			   本月机型负向口碑, 
			   上月机型负向口碑,
               机型负向口碑变化,
               变动比率 
			   from temp_ana_model_abnormal_nature_month ;
	"""

	sql_2 =  """
			select * from temp_ana_model_abnormal_market_month ; 
	"""
	return (sql_1,sql_2)


# def auto_analysis_series_change(partial_sql,startdate,enddate):
# 	#自动提取分析表数据
	
