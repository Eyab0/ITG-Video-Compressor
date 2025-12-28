@echo off
REM Main build script - runs from project root
REM This script calls the build script in build_scripts folder

cd /d "%~dp0"
call build_scripts\build.bat

