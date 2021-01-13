:: 提取MYSQL计算结果,包括有整体，电商评论，分析结果
pushd %~dp0
cd code
python 4-fetch_overall.py
python 5-fetch_competitives.py
python 6-fetch_analysis.py
popd
pause