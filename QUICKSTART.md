# 🚀 Quick Start Guide

## Prerequisites
- Node.js 18+ 
- Python 3.9+ (⚠️ **Important**: Use Python 3.9, not 3.13 for better compatibility)
- Git
- **Windows users**: See [PYTHON_SETUP.md](PYTHON_SETUP.md) for detailed Python installation guide

## Option 1: Automatic Installation (Recommended)

### Windows
```bash
# Run the installation script
install-windows.bat
```

### Linux/Mac
```bash
# Make script executable and run
chmod +x install.sh
./install.sh
```

## Option 2: Manual Installation

### 1. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
**Frontend will be available at:** http://localhost:3000

### 2. Backend Setup
```bash
cd backend
npm install
npm run dev
```
**Backend API will be available at:** http://localhost:5000

### 3. ML Service Setup
```bash
cd ml-services
pip install -r requirements-simple.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
uvicorn app.main:app --reload --port 8000
```
**ML Service will be available at:** http://localhost:8000


## 🎯 How to Use

1. **Open the application** at http://localhost:3000
2. **Choose your input method:**
   - **Upload Resume**: Drag & drop your PDF/DOC/DOCX file
   - **Select Interests**: Choose from categorized skills and interests
3. **Click "Get My Recommendations"**
4. **View your personalized matches** with match scores and details

## 🔧 Troubleshooting

### Common Issues

**Frontend won't start:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Backend connection issues:**
- Check if backend is running on port 5000
- Verify CORS settings in backend/src/server.js

**ML Service errors:**
```bash
cd ml-services
pip install --upgrade -r requirements-simple.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

**File upload issues:**
- Ensure file is PDF, DOC, or DOCX
- Check file size (max 10MB)
- Verify backend is running

## 📱 Features

- ✅ **Resume Upload** with AI parsing
- ✅ **Interest Selection** from curated dataset  
- ✅ **Smart Recommendations** with match scores
- ✅ **Company Database** with 5+ companies
- ✅ **Responsive Design** for all devices
- ✅ **Modern UI** with TypeScript and SCSS

## 🆘 Need Help?

1. Check the logs in your terminal
2. Review the full [SETUP.md](SETUP.md) guide
3. Ensure all services are running
4. Check browser console for errors

## 🎉 Success!

Once all services are running, you should see:
- Frontend: Beautiful landing page with upload/interest options
- Backend: API endpoints responding at /api/health
- ML Service: FastAPI docs at /docs

**Happy coding! 🚀**
