@echo off

title export template£º%1
mode con cols=100 lines=1500
color 3

%~dp0\..\exporter\TableExporter\TableExporter.exe %*

pause&exit