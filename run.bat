@echo off
chcp 65001 > nul
title EmailFlow Tester Launcher
cls

echo =================================================================
echo   EMAILFLOW TESTER - TU DONG GUI EMAIL THU NGHIEM PHAN LOAI
echo =================================================================
echo.

:: Kiem tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren he thong!
    echo Vui long cai dat Python 3.9 tro len va tich hop vao PATH.
    pause
    exit /b
)

:: Kiem tra va cai dat thu vien
echo [1/2] Dang kiem tra thu vien phu thuoc...
pip install -r requirements.txt --quiet

echo [2/2] San sang!
echo.
echo -----------------------------------------------------------------
echo Vui long chon che do khoi chay:
echo   [1] Giao dien Web Dashboard (Streamlit UI - Khuyen dung)
echo   [2] Giao dien Dong lenh (CLI Interactive Menu)
echo   [3] Chay Test nhanh Gia lap (Dry Run 20 Email)
echo   [4] Xuat 10 file mau .EML ra thu muc cuc bo
echo   [0] Thoat
echo -----------------------------------------------------------------
echo.

set /p choice="Nhap lua chon cua ban [1-4, 0]: "

if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3
if "%choice%"=="4" goto option4
if "%choice%"=="0" goto option0

echo Lua chon khong hop le!
pause
exit /b

:option1
echo.
echo Dang khoi chay Streamlit Web Dashboard...
streamlit run app.py
pause
exit /b

:option2
echo.
python cli.py
pause
exit /b

:option3
echo.
python cli.py --target test-target@emailflow.internal --count 20 --dry-run
pause
exit /b

:option4
echo.
python cli.py --target eml-test@emailflow.internal --count 10 --export-eml
pause
exit /b

:option0
echo Tam biet!
exit /b
