if not exist "stored_data(alert)\output(alert)" mkdir "stored_data(alert)\processed_details(alert)"
::clean the  "stored_data(alert)\processed_details(alert)" folder
del /Q "stored_data(alert)\processed_details(alert)\"*
::generate warning data, data only contains if_warning == True
START /B /WAIT DataHandler.exe -c "config_calc_details(India)" -i "stored_data(alert)\processed_data(alert)" -o "stored_data(alert)\processed_details(alert)"
if "%errorLevel%"=="1" goto :end
::generate word frequency
START /B /WAIT DataHandler.exe -c "config_calc_words(India)" -i "stored_data(alert)\processed_details(alert)" -o "stored_data(alert)\output(alert)"
if "%errorLevel%"=="1" goto :end
pause