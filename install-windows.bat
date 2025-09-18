@echo off
echo Installing AI Internship Recommendation Engine for Windows...
echo.

echo Installing Frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo Frontend installation failed!
    pause
    exit /b 1
)
cd ..

echo.
echo Installing Backend dependencies...
cd backend
call npm install
if %errorlevel% neq 0 (
    echo Backend installation failed!
    pause
    exit /b 1
)
cd ..

echo.
echo Installing ML Service dependencies (Windows-compatible)...
cd ml-services

echo Installing ML Service dependencies...
call pip install -r requirements-simple.txt
if %errorlevel% neq 0 (
    echo Installation failed, trying alternative approach...
    echo.
    echo Installing basic packages...
    call pip install fastapi uvicorn python-multipart pydantic python-dotenv
    call pip install PyPDF2 python-docx
    call pip install nltk regex requests loguru
    if %errorlevel% neq 0 (
        echo ML Service installation failed!
        echo Please check Python version (use 3.9) and install Visual Studio Build Tools
        pause
        exit /b 1
    )
)

echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

echo.
echo Note: For full ML capabilities, consider using conda environment
echo or installing Visual Studio Build Tools for better package compatibility
echo.

cd ..

echo.
echo Installation completed!
echo.
echo To start the application:
echo 1. Frontend: cd frontend && npm run dev
echo 2. Backend: cd backend && npm run dev  
echo 3. ML Service: cd ml-services && uvicorn app.main:app --reload --port 8000
echo.
echo All services ready to start!
echo.
pause
