@echo off
echo Checking Python installation...
echo.

echo Current Python version:
python --version
echo.

echo Checking if Python 3.9 is available:
py -3.9 --version 2>nul
if %errorlevel% equ 0 (
    echo ✅ Python 3.9 found!
    echo.
    echo To use Python 3.9, run:
    echo   py -3.9 -m pip install -r ml-services/requirements-simple.txt
    echo   py -3.9 -m uvicorn ml-services.app.main:app --reload --port 8000
) else (
    echo ❌ Python 3.9 not found
    echo.
    echo Please install Python 3.9 from:
    echo https://www.python.org/downloads/release/python-3913/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
)

echo.
echo Current pip version:
pip --version
echo.

echo Checking if packages are installed:
python -c "import fastapi" 2>nul
if %errorlevel% equ 0 (
    echo ✅ FastAPI is installed
) else (
    echo ❌ FastAPI not found
)

python -c "import uvicorn" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Uvicorn is installed
) else (
    echo ❌ Uvicorn not found
)

echo.
echo For detailed setup instructions, see PYTHON_SETUP.md
echo.
pause
