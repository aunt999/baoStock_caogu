@echo off
chcp 65001 >nul
title 量化交易回测环境

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║       量化交易回测环境 - QUANTAXIS + Backtrader       ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo  已安装组件:
echo    - QUANTAXIS 1.10.19
echo    - Backtrader 1.9.78.123
echo    - Akshare 1.18.59
echo.
echo  快速命令:
echo    1 - 运行回测演示（模拟数据）
echo    2 - 运行回测演示（真实数据）
echo    3 - 启动 Python 交互环境
echo    4 - 查看使用指南
echo    Q - 退出
echo.

set /p choice="请选择: "

if "%choice%"=="1" (
    echo.
    echo 运行回测演示（模拟数据）...
    echo.
    F:\FilesData\QUANTAXIS\venv\Scripts\python.exe F:\FilesData\QUANTAXIS\strategy_demo_local.py
    pause
    goto :eof
)

if "%choice%"=="2" (
    echo.
    echo 运行回测演示（真实数据）...
    echo.
    F:\FilesData\QUANTAXIS\venv\Scripts\python.exe F:\FilesData\QUANTAXIS\strategy_demo.py
    pause
    goto :eof
)

if "%choice%"=="3" (
    echo.
    echo 启动 Python 交互环境...
    echo.
    F:\FilesData\QUANTAXIS\venv\Scripts\python.exe -i
    goto :eof
)

if "%choice%"=="4" (
    notepad F:\FilesData\QUANTAXIS\量化交易完整指南.md
    goto :eof
)

if /i "%choice%"=="Q" (
    exit
)

echo 无效选择
pause
