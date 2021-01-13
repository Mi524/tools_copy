:: 处理售后部分数据
pushd %~dp0
cd code
python 1-aftersale.py
:: 写入整体数据(从BI导出的售后，从VOC系统导出的意见反馈,呼叫中心)
python 2-write2sql_overall.py
popd
pause