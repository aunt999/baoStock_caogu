@echo off
chcp 65001 >nul
title MongoDB 服务管理

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║           MongoDB 服务管理工具                        ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo 1 - 启动 MongoDB
echo 2 - 停止 MongoDB
echo 3 - 查看状态
echo 4 - 重启 MongoDB
echo Q - 退出
echo.

set /p choice="请选择: "

if ""%choice%""==""1"" goto start
if ""%choice%""==""2"" goto stop
if ""%choice%""==""3"" goto status
if ""%choice%""==""4"" goto restart
if /i ""%choice%""==""Q"" exit

:start
echo.
echo 启动 MongoDB 服务...
net start MongoDB
echo.
pause
goto :eof

:stop
echo.
echo 停止 MongoDB 服务...
net stop MongoDB
echo.
pause
goto :eof

:status
echo.
sc query MongoDB
echo.
pause
goto :eof

:restart
echo.
echo 重启 MongoDB 服务...
net stop MongoDB
timeout /t 2 >nul
net start MongoDB
echo.
pause
goto :eof
