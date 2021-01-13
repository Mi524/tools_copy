:: 写入产品信息表
pushd %~dp0
cd code
python write2sql_model_info.py
popd
pause