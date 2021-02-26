cd %~dp0
::调用脚本，填写文档路径和VBA代码路径等参数,运行时尽量关闭EXCEL，否则可能出现资源冲突运行失败的情况
::参数-v VBA文件夹，-i 需要处理的EXCEL文件夹，-o 输出结果文件夹，-m 需要运行的宏名称(Sub名称)
START /B /WAIT execute_vba.exe -v "VBA" -i "input_dir" -o "output_dir" -m "macroScript"
Pause