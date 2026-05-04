@echo off
title QUANTAXIS Python Environment
cd /d "F:\FilesData\QUANTAXIS"
echo ========================================
echo     QUANTAXIS v1.10.19 Python 环境
echo ========================================
echo.
echo 按 Ctrl+C 退出，或关闭窗口
echo.
F:\FilesData\QUANTAXIS\venv\Scripts\python.exe -c "import sys; _o=sys.exit; sys.exit=lambda c=0: None; import QUANTAXIS; sys.exit=_o; print('QUANTAXIS', QUANTAXIS.__version__, 'Ready!')" 2>nul
echo.
F:\FilesData\QUANTAXIS\venv\Scripts\python.exe -i