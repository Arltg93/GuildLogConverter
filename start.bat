@echo off
setlocal enabledelayedexpansion

:choosePlayer
echo.
set playername=
set /p playername=Spielername:
cls

python GuildWar.py %playername%
goto choosePlayer
pause