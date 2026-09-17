@echo off
py -3 "%~dp0tools\build_gui.py"
if errorlevel 1 echo Build failed. Check the message above. Python 3.10 or newer is required.
pause
