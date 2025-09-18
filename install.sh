#!/bin/bash

echo "Installing AI Internship Recommendation Engine..."
echo

# Install Frontend dependencies
echo "Installing Frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "Frontend installation failed!"
    exit 1
fi
cd ..

# Install Backend dependencies
echo "Installing Backend dependencies..."
cd backend
npm install
if [ $? -ne 0 ]; then
    echo "Backend installation failed!"
    exit 1
fi
cd ..

# Install ML Service dependencies
echo "Installing ML Service dependencies..."
cd ml-services
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ML Service installation failed!"
    exit 1
fi
cd ..

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

echo
echo "Installation completed successfully!"
echo
echo "To start the application:"
echo "1. Frontend: cd frontend && npm run dev"
echo "2. Backend: cd backend && npm run dev"
echo "3. ML Service: cd ml-services && uvicorn app.main:app --reload --port 8000"
echo
echo "All services ready to start!"
echo
