:: 运行计算程序，整个过程大概需要20分钟
:: 如果需要计算历史的实销月数据，比如当前是2月，想取出1月底的实销月数据时：
:: 可以只从3-3开始运行，3-1,3-2可以用两个冒号注释掉
pushd %~dp0
cd code
python 3-1-run_overall.py
python 3-2-run_ecommerce.py
python 3-3-run_market_month.py 
python 3-4-run_analysis.py 
popd
pause