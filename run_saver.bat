@echo off
echo Starting Simple Facebook Image Saving Automation...
echo Attaching to Virtual Environment...
call .\env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Could not activate virtual environment 'env'.
    echo Please make sure you have created it using 'python -m venv env'.
    pause
    exit /b %errorlevel%
)
python main.py
pause
