@echo off
cls
color 0D
title Cosmetz by Thegamerprogrammer

echo  ______     ______     ______     __    __     ______     ______   ______   
echo /\  ___\   /\  __ \   /\  ___\   /\ "-./  \   /\  ___\   /\__  _\ /\___  \ 
echo \ \ \____  \ \ \/\ \  \ \___  \  \ \ \-./\ \  \ \  __\   \/_/\ \/ \/_/  /__  
echo  \ \_____\  \ \_____\  \/_____/   \ \_\ \ \_\  \ \_____\    \ \_\   /\_____\
echo   \/_____/   \/_____/   \/_____/   \/_/  \/_/   \/_____/     \/_/   \/_____/

goto checkAdmin

:checkAdmin
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B

:gotAdmin
if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
pushd "%CD%"
CD /D "%~dp0"
goto splash

:splash
echo PC/Laptop Performance Booster
echo Supported Versions: Windows 11/10/7
pause
goto startOptimization

:startOptimization
echo Initializing...
timeout 3

echo This program will:
echo - Change power plan based on Windows version
echo - Clear temporary files
echo - Optimize memory settings
echo - Disable unnecessary features
echo - Reset network settings
echo - Repair corrupted files
echo - Restart necessary services
echo - Restart Windows
pause
cls
color 0A

set /p driveType=Do you have an SSD (1) or HDD (2)?:
set /p winVersion=Enter your Windows version (11/10/7):

if %winVersion%==11 goto setUltimatePower
if %winVersion%==10 goto setUltimatePower
if %winVersion%==7 goto setHighPerf

goto optimizePC

:setUltimatePower
echo Setting power plan to Ultimate Performance...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61
timeout 3
goto optimizePC

:setHighPerf
echo Setting power plan to High Performance...
powercfg -setactive scheme_min
timeout 3
goto optimizePC

:optimizePC
cls
echo Clearing temporary files...
del /q/f/s %temp%\*
echo Temporary files cleared!
timeout 2

color 0D
echo Optimizing memory usage...
fsutil behavior set memoryusage 2
bcdedit /set disabledynamictick yes
bcdedit /set useplatformtick yes
echo Memory optimizations applied!
timeout 2

color 0C
echo Disabling Search Indexing...
sc stop "wsearch" && sc config "wsearch" start=disabled
echo Search Indexing Disabled!
timeout 2

color 0D
echo Resetting Network Settings...
ipconfig /release
ipconfig /flushdns
ipconfig /renew
netsh int ip reset
netsh winsock reset
echo Network settings reset!
timeout 2

:clearCache
color 0D
echo Clearing Microsoft Store Cache...
start /wait WSReset.exe
echo Cache cleared!
timeout 2

:deleteJunk
color 0D
echo Deleting junk files...
del /f /s /q %systemdrive%\*.tmp
del /f /s /q %systemdrive%\*.log
del /f /s /q %systemdrive%\*.bak
del /f /s /q %windir%\prefetch\*.*
echo Junk files deleted!
timeout 3

:scanAndRepair
color 0D
echo Repairing system files (this may take a while)...
DISM.exe /Online /Cleanup-Image /RestoreHealth
sfc /scannow
echo System repair complete!
timeout 3

:diskDefrag
if %driveType%==2 (
    echo Running disk check on HDD...
    chkdsk /f /r
)
echo Defragmenting drives...
defrag /C
echo Defragmentation complete!
timeout 3

:restartServices
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver
net start wuauserv
net start cryptSvc
net start bits
net start msiserver
echo Services restarted!
timeout 3

:finalStep
echo Restarting Windows in 10 seconds...
timeout 10
shutdown /r
