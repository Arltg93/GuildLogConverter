@echo off
setlocal enabledelayedexpansion

:choosePlayer
echo.
set playername=
set /p playername=Spielername:
cls


if "%playername%" == "" (
    python GuildWar.py
) else (
    python GuildWar.py -p %playername%
)
goto choosePlayer
pause