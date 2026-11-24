@echo off
cd /d "%~dp0"
echo === StudyPath setup ===
if not exist venv python -m venv venv
call venv\Scripts\activate
python -m pip install -r requirements.txt
if errorlevel 1 goto fail
python setup.py
if errorlevel 1 goto fail
echo.
echo Setup finished. Double-click start.bat to run the app.
pause
exit /b 0

:fail
echo.
echo Setup did not finish. Read the message above.
pause
exit /b 1