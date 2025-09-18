@echo off
echo Installing AI Internship Recommendation Engine...
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
echo Installing ML Service dependencies...
cd ml-services
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ML Service installation failed!
    pause
    exit /b 1
)
cd ..

echo.
echo Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

echo.
echo Installation completed successfully!
echo.
echo To start the application:
echo 1. Frontend: cd frontend && npm run dev
echo 2. Backend: cd backend && npm run dev  
echo 3. ML Service: cd ml-services && uvicorn app.main:app --reload --port 8000
echo.
echo All services ready to start!
echo.
pause
