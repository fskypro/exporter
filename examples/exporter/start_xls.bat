@echo off

title export template£º%1
mode con cols=100 lines=1500
color 3


%~dp0\..\exporter\TableExporter\TableExporter.exe %*


setlocal enabledelayedexpansion
set a=%*
set b=%1
set c=!a:%b%=!
set c=%c:~1%


if {"%c%"}=={"~1"} goto :end
start call %c%


:end
pause&exit
