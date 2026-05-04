@echo off
chcp 65001 >nul
title 股票量化分析系统
echo.
echo   ================================
echo     股票量化分析系统 - 启动中...
echo   ================================
echo.
F:\FilesData\QUANTAXIS\venv\Scripts\python.exe F:\FilesData\QUANTAXIS\stock_gui.py
pause
