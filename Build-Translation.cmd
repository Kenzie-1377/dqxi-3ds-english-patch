@echo off
if not exist "%~dp0dist\DQXI-English-Translation-Builder.exe" (
 echo First run Build-Windows-Exe.ps1, or download the verified 0.6.0 EXE from GitHub Releases.
 pause
 exit /b 1
)
start "" "%~dp0dist\DQXI-English-Translation-Builder.exe"
