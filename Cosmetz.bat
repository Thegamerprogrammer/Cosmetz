@echo off

cls

color 0d

title Cosmetz by Thegamerprogrammer

echo  ______     ______     ______     __    __     ______     ______   ______   
echo /\  ___\   /\  __ \   /\  ___\   /\ "-./  \   /\  ___\   /\__  _\ /\___  \ 
echo \ \ \____  \ \ \/\ \  \ \___  \  \ \ \-./\ \  \ \  __\   \/_/\ \/ \/_/  /__  
echo  \ \_____\  \ \_____\  \/\_____\  \ \_\ \ \_\  \ \_____\    \ \_\   /\_____\
echo   \/_____/   \/_____/   \/_____/   \/_/  \/_/   \/_____/     \/_/   \/_____/

goto checkAdmin

:checkAdmin
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
:: If error flag set, we do not have admin.
:: If no admin, reqeust admin via VBS script
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
:gotAdmin
:: delete script after getting admin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"
    goto splash

:splash
echo Pc/Laptop Performance Booster
echo Supported Versions Win 11/10/7
pause
goto PermsConfirmedStartProgram



:PermsConfirmedStartProgram
echo initializing...

timeout 5

cls
echo press enter to optimize pc
pause

echo changing powerplan

set /p answer=Do you have windows 11/10/7? Type The Version Alone!: 
if %answer%==11 goto cfgulti
if %answer%==10 goto cfgulti
if %answer%==7 goto cfghp
if %answer%==4 goto OptimisePc

:cfgulti
powercfg -duplicatescheme 03bc31d9-dd93-42db-8e4e-f5367c08a06b
powercfg /setactive 03bc31d9-dd93-42db-8e4e-f5367c08a06b
echo changed powerplan to Ultimate Performance Only available to Windows 10 and above!
timeout 4
goto OptimisePc


:cfghp
powercfg -getactivescheme
powercfg -setactive scheme_min

echo changed power plan to high performance!
timeout 4
goto OptimisePc


:OptimisePc
echo clearing temporary files

timeout 10

del /q/f/s %temp%\*

echo cleared temporary files

echo doing additional changes

timeout 5

Fsutil behavior query memoryusage

Fsutil behavior set memoryusage 2

bcdedit /deletevalue useplatformclock

bcdedit /set disabledynamictick yes

bcdedit /set useplatformtick yes

echo Disabling Search Indexing...
echo Dont close THIS WINDOW!

timeout 5

sc stop "wsearch" && sc config "wsearch" start=disabled

echo Disabled Search Indexing!

echo Dont close THIS WINDOW!

timeout 5

echo Resetting Network Settings
echo Dont close THIS WINDOW!

timeout 9

ipconfig /release
echo stage 1 done
ipconfig /flushdns
echo stage 2 done
ipconfig /renew
echo stage 3 done
echo Dont close THIS WINDOW!
echo if The Program Says To Restart The System Now DONT!
timeout  4
cls
echo initiating netsh commands
timeout 1
netsh int ip reset
echo Stage 1 of netsh reset completed
netsh winsock reset
echo Stage 2 of netsh winsock reset completed
echo Dont close THIS WINDOW!
echo if The Program Says To Restart The System Now DONT!
timeout 4

set /p answer=Do you have windows 11/10/7? Type The Version Alone This Feature Wont Work On Win 7 So If You are On Windows 7 Type No!: 
if %answer%==11 goto ClearMSCache
if %answer%==10 goto ClearMSCache
if %answer%==7 goto Continue


:ClearMSCache
echo clearing Ms Store Cache
echo Dont close THIS WINDOW!
timeout 2
start WSReset.exe
echo cleared Ms Store Cache
timeout 5
goto Continue


:Continue
echo Clearing Junk Files Might Take A While DONT SWITCH OF YOUR COMOUTER OR TURN OFF THIS PROGRAM!

echo Clearing junk Files May Take A While Depending On Your Hardware! 
timeout 4

cls

echo deleting Temp files
timeout 2
del /f /s /q %systemdrive%\*.tmp

cls
echo Deleted Temp files
timeout 2

echo deleting mp files
timeout 1

del /f /s /q %systemdrive%\*._mp

cls
echo Deleted _mp files 
timeout 2

echo deleting log files
timeout 1

del /f /s /q %systemdrive%\*.log 

cls
echo deleted log files
timeout 2

echo deleting gid files
timeout 1

del /f /s /q %systemdrive%\*.gid 

cls
echo deleted gid files
timeout 2

echo deleting chk files
timeout 1

del /f /s /q %systemdrive%\*.chk

cls
echo deleted chk files
timeout 2

echo deleting old files
timeout 1

del /f /s /q %systemdrive%\*.old

cls
echo deleted old files
timeout 2

echo deleting RecycleBin files
timeout 1

del /f /s /q %systemdrive%\recycled\*.*

cls
echo deleted RecycleBin files
timeout 2

echo deleting bak files
timeout 1

del /f /s /q %windir%\*.bak

cls
echo deletd bak files
cls

echo deleting prefetch and temp files
timeout 1

del /f /s /q %windir%\prefetch\*.* rd /s /q %windir%\temp & md %windir%\temp

cls
echo deleted prefetch and temp files
timeout 2

echo Cache Files and Temporary files deleted

echo running SystemFileCheckersfc May Take Some Time aprrox 30mins
echo do not close this program! until you see System Scan Complete.

timeout 2

sfc /scannow

echo System Scan Complete

timeout 5

echo Restarting Windows services!

timeout 1

net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver

echo Starting Windows services!

timeout 1

net start wuauserv
net start cryptSvc
net start bits
net start msiserver

timeout 5

echo your pc needs to restart now or the proccess will be incomplete
echo restaring in 10 seconds
echo Don't Close The Program!
timeout 10
shutdown /r
