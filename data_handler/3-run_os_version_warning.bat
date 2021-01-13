cd %~dp0

if not exist "stored_data(alert)\input_data(alert)" mkdir "stored_data(alert)\input_data(alert)"
if not exist "stored_data(alert)\processed_data(alert)" mkdir "stored_data(alert)\processed_data(alert)"
if not exist "stored_data(alert)\output(alert)" mkdir "stored_data(alert)\output(alert)"
::clear folder stored_data(OS update alert)
del /S /Q "stored_data(OS update alert)"
:: incase no folders
if not exist "stored_data(OS update alert)\step1" mkdir "stored_data(OS update alert)\step1"
if not exist "stored_data(OS update alert)\step2" mkdir "stored_data(OS update alert)\step2"
if not exist "stored_data(OS update alert)\step3" mkdir "stored_data(OS update alert)\step3"
if not exist "stored_data(OS update alert)\step4" mkdir "stored_data(OS update alert)\step4"
if not exist "stored_data(OS update alert)\step5" mkdir "stored_data(OS update alert)\step5"
if not exist "stored_data(OS update alert)\step5" mkdir "stored_data(OS update alert)\step6"

::run statistic config to get statistic result for OS version, type, model
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step1 version" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(OS update alert)\step1"
if "%errorLevel%"=="1" goto :end
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step2 type" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(OS update alert)\step2"
if "%errorLevel%"=="1" goto :end
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step3 model" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(OS update alert)\step3"
if "%errorLevel%"=="1" goto :end
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step4 modelOS" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(OS update alert)\step4"
if "%errorLevel%"=="1" goto :end

START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step5 concat2" -i "stored_data(OS update alert)\step2" -o "stored_data(OS update alert)\step5"
if "%errorLevel%"=="1" goto :end
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step5 concat3" -i "stored_data(OS update alert)\step3" -o "stored_data(OS update alert)\step5"
if "%errorLevel%"=="1" goto :end
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step5 concat4" -i "stored_data(OS update alert)\step4" -o "stored_data(OS update alert)\step5"
if "%errorLevel%"=="1" goto :end
::Move step 4 results to require table, step1 result left join step 4(see sheet "matching" process in step5 config)
MOVE "stored_data(OS update alert)\step5\"*.*  "require_tables\"
::final step
START /B /WAIT DataHandler.exe -c "config_calc_amount(India) - OS calc step6" -i "stored_data(OS update alert)\step1" -o "stored_data(OS update alert)\step6"
if "%errorLevel%"=="1" goto :end

::Delete all the calc result from require_tables folder 
Del "require_tables\"calc_amount(India)*.xlsx
:end
Pause