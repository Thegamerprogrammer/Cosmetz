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

echo What This Program Is Going to do:
echo Change Powerplan According To Windows Version
echo Clear Temporary Files
echo Raises The Limit Of Paged Pool Memory
echo Disables Ticks
echo Disables Search Indexing
echo Clears Network Cache
echo Clears Ms Store Cache
echo Scans And Repairs Curropted Files
echo Restarts Services
echo Restarts Windows
pause
cls
echo press any key to optimize pc
pause

echo changing powerplan

echo If You Are Not Sure What Type Of Drive You Have Open Task Manager And Go to Peformance.
set /p ans=Do You Have An SSD Solid State Drive Or A HDD Hard Disk Drive? Type 1 For SSD And 2 For HDD:
echo %ans%

set /p answer=Do you have windows 11/10/7? Type The Version Alone!: 
if %answer%==11 goto cfgulti
if %answer%==10 goto cfgulti
if %answer%==7 goto cfghp
if %answer%==4 goto OptimisePc
if %answer%==1 goto OptimisePc

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
cls
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
cls

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
goto CheckSysCompactibility


:CheckSysCompactibility
echo Checking system Compactibility!
echo %answer% 
if %answer%==11 goto ClearMSCache
if %answer%==10 goto ClearMSCache
if %answer%==7 goto Continue
if %answer%==4 goto ClearMSCache
if %answer%==1 goto Continue


:ClearMSCache
echo clearing Ms Store Cache
echo Dont close THIS WINDOW!
timeout 2
start WSReset.exe
echo cleared Ms Store Cache
timeout 5
goto Continue


:Continue
echo Clearing Junk Files Might Take A While DONT SWITCH OF YOUR COMPUTER OR EXIT THIS PROGRAM!

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
echo deleted bak files
cls

echo deleting prefetch and temp files
timeout 1

del /f /s /q %windir%\prefetch\*.* rd /s /q %windir%\temp & md %windir%\temp

cls
echo deleted prefetch and temp files
timeout 2

echo Cache Files and Temporary files deleted

echo Scanning And Repairing Corrupted Files.
echo May Take Some Time..

timeout 2

DISM.exe /Online /Cleanup-Image /Restorehealth

echo Restored System Health

echo Running System File Checker

sfc /scannow

echo System Scan Complete

echo Do You Have An SSD Drive or HDD Drive?
echo Type 1 For SSD Drive and 2 For HDD Drive
goto Checkhdd

:Checkhdd
if %ans%==2 goto chk
if %ans%==1 goto nochk

:chk
echo Detecting Disk Errors On HDD
echo if You Are Prompted with CHKDSK CANNOT RUN BECAUSE THE VOLUME IS IN USE BY ANOTHER PROCESS. WOULD YOU LIKE TO SCHEDULE THIS VOLUME TO BE CHECKED THE NEXT TIME THE SYSTEM RESTARTS?
echo Then Type Y and press enter

chkdsk /f /r
echo DONT CLOSE THIS WINDOW
timeout 1
goto nochk

:nochk
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

echo Windows needs to restart Now
echo DONT CLOSE THIS WINDOW OR SYSTEM MAY BE UNSTABLE!
echo restaring in 10 seconds
echo Don't Close The Program!
timeout 10
shutdown /r