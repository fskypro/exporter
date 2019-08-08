python.exe setup.py py2exe -d

@move .\bin\main_d.exe ..\TableExporter\TableExporter.exe
@copy .\scripts\tpls\tpl_base.py ..\TableExporter\tpl_base.py /Y
@copy .\scripts\tpls\样板.py ..\TableExporter\样板.py /Y
@copy .\config_d.xml ..\TableExporter\config.xml /Y
@copy .\bin.xml ..\TableExporter\bin.xml /Y
@xcopy .\local\*.xml ..\TableExporter\local\ /s/Y

@echo 成功&PAUSE>nul
