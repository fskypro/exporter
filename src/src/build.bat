python.exe setup.py py2exe

@move .\bin\main.exe ..\TableExporter\TableExporter.exe
@copy .\scripts\tpls\tpl_base.py ..\TableExporter\tpl_base.py /Y
@copy .\scripts\tpls\����.py ..\TableExporter\����.py /Y
@copy .\config.xml ..\TableExporter\config.xml /Y
@copy .\bin.xml ..\TableExporter\bin.xml /Y
@xcopy .\local\*.xml ..\TableExporter\local\ /s/Y

@echo �ɹ�&PAUSE>nul
