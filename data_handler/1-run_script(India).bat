:: You need to put the raw data to input_data folder then run this batch script, 
:: after the script is finished, you will get the alert output in stored_data(alert)\output(alert) folder
cd %~dp0
::create folders to store data for the script
if not exist "stored_data(alert)\input_data(alert)" mkdir "stored_data(alert)\input_data(alert)"
if not exist "stored_data(alert)\processed_data(alert)" mkdir "stored_data(alert)\processed_data(alert)"
if not exist "stored_data(alert)\output(alert)" mkdir "stored_data(alert)\output(alert)"

::1. Run DataHandler.exe and select the config folder to process raw data, so that we can get processed result
START /B /WAIT DataHandler.exe -c "config_process_data(India)" -i "input_data" -o "stored_data(alert)\processed_data(alert)"
if "%errorLevel%"=="1" goto :end
::2. run statistic config to get statistic result
START /B /WAIT DataHandler.exe -c "config_calc_amount(India)" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(alert)\output(alert)"
if "%errorLevel%"=="1" goto :end
::2.1  get detail warning data(only require in other countries)	
START /B /WAIT DataHandler.exe -c "config_calc_details(India)" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(alert)\processed_details(alert)"
if "%errorLevel%"=="1" goto :end
::3. Move input raw data to stored_data(alert)\input_data(alert)
MOVE "input_data\"*.*  "stored_data(alert)\input_data(alert)\"
:end
pause