@echo off

title export template��%1
mode con cols=100 lines=1500
color 3

exporter\TableExporter\TableExporter.exe "%1"

pause&exit