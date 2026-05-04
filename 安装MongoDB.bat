@echo off
chcp 65001 >nul
title MongoDB 安装助手

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║              MongoDB 手动安装指南                     ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo  网络下载受限，请手动下载 MongoDB:
echo.
echo  【步骤1】打开浏览器访问:
echo    https://www.mongodb.com/try/download/community
echo.
echo  【步骤2】选择版本:
echo    Version: 7.0.15 (或最新)
echo    Platform: Windows
echo    Package: zip
echo.
echo  【步骤3】点击 Download 开始下载
echo.
echo  【步骤4】下载完成后，将 zip 文件放到:
echo    D:\ProgramData\MongoDB\
echo.
echo  【步骤5】解压 zip 文件到当前目录
echo.
echo  【步骤6】运行此脚本继续安装:
echo    F:\FilesData\QUANTAXIS\安装MongoDB.bat
echo.
echo ──────────────────────────────────────────────────────
echo.
pause

:: 检查 MongoDB 是否已安装
set MONGO_HOME=D:\ProgramData\MongoDB
set MONGO_BIN=%MONGO_HOME%\bin

if exist "%MONGO_BIN%\mongod.exe" (
    echo [OK] 找到 mongod.exe
    goto :install
)

:: 检查子目录
for /d %%d in ("%MONGO_HOME%\mongodb-*") do (
    if exist "%%d\bin\mongod.exe" (
        echo [OK] 找到 MongoDB 在 %%d
        set MONGO_BIN=%%d\bin
        goto :install
    )
)

echo.
echo [错误] 未找到 mongod.exe
echo 请确保已解压 MongoDB zip 文件到 D:\ProgramData\MongoDB\
echo.
pause
exit /b 1

:install
echo.
echo ══════════════════════════════════════════════════════
echo 开始配置 MongoDB...
echo ══════════════════════════════════════════════════════
echo.

:: 创建数据和日志目录
if not exist "%MONGO_HOME%\data" mkdir "%MONGO_HOME%\data"
if not exist "%MONGO_HOME%\log" mkdir "%MONGO_HOME%\log"
echo [OK] 创建数据目录: %MONGO_HOME%\data
echo [OK] 创建日志目录: %MONGO_HOME%\log

:: 创建配置文件
echo storage: > "%MONGO_HOME%\mongod.cfg"
echo   dbPath: %MONGO_HOME%\data >> "%MONGO_HOME%\mongod.cfg"
echo systemLog: >> "%MONGO_HOME%\mongod.cfg"
echo   destination: file >> "%MONGO_HOME%\mongod.cfg"
echo   path: %MONGO_HOME%\log\mongod.log >> "%MONGO_HOME%\mongod.cfg"
echo net: >> "%MONGO_HOME%\mongod.cfg"
echo   port: 27017 >> "%MONGO_HOME%\mongod.cfg"
echo   bindIp: 127.0.0.1 >> "%MONGO_HOME%\mongod.cfg"
echo [OK] 创建配置文件: %MONGO_HOME%\mongod.cfg

:: 安装为 Windows 服务
echo.
echo 安装 MongoDB 为 Windows 服务...
"%MONGO_BIN%\mongod.exe" --config "%MONGO_HOME%\mongod.cfg" --install
echo [OK] 服务安装完成

:: 启动服务
echo.
echo 启动 MongoDB 服务...
net start MongoDB
if %errorlevel%==0 (
    echo [OK] MongoDB 服务已启动
) else (
    echo [警告] 服务启动失败，尝试手动启动...
    start "" "%MONGO_BIN%\mongod.exe" --dbpath "%MONGO_HOME%\data"
    echo [OK] MongoDB 已手动启动
)

:: 验证
echo.
echo 验证 MongoDB 连接...
timeout /t 3 >nul
"%MONGO_BIN%\mongosh.exe" --eval "db.version()" 2>nul
if %errorlevel%==0 (
    echo [OK] MongoDB 连接成功!
) else (
    echo [警告] 无法连接，请检查日志: %MONGO_HOME%\log\mongod.log
)

echo.
echo ══════════════════════════════════════════════════════
echo MongoDB 安装完成!
echo ══════════════════════════════════════════════════════
echo.
echo  数据目录: %MONGO_HOME%\data
echo  日志文件: %MONGO_HOME%\log\mongod.log
echo  配置文件: %MONGO_HOME%\mongod.cfg
echo  端口: 27017
echo.
echo  服务命令:
echo    启动: net start MongoDB
echo    停止: net stop MongoDB
echo.
pause
