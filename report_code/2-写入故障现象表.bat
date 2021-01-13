pushd %~dp0
cd code
:: 将检查好的故障现象数量写入MYSQL
python 2-write2sql_ecommerce.py
popd
pause