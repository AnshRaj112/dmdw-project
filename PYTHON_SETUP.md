# 🐍 Python Setup Guide

## The Problem
Python 3.13 is very new and many packages don't have pre-compiled wheels yet, causing installation issues.

## ✅ Solutions

### Option 1: Use Python 3.9 (Recommended)

1. **Download Python 3.9:**
   - Go to: https://www.python.org/downloads/release/python-3913/
   - Download Windows installer (64-bit)
   - **Important**: Check "Add Python to PATH" during installation

2. **Verify Installation:**
   ```bash
   python --version
   # Should show Python 3.9.x
   ```

3. **Install Packages:**
   ```bash
   cd ml-services
   pip install -r requirements-simple.txt
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

4. **Run ML Service:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Option 2: Use Conda (Alternative)

1. **Install Miniconda:**
   - Download from: https://docs.conda.io/en/latest/miniconda.html
   - Install and restart terminal

2. **Create Environment:**
   ```bash
   conda create -n internship-recommender python=3.9
   conda activate internship-recommender
   ```

3. **Install Packages:**
   ```bash
   cd ml-services
   pip install -r requirements-simple.txt
   ```

4. **Run ML Service:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Option 3: Use Virtual Environment

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Packages:**
   ```bash
   cd ml-services
   pip install -r requirements-simple.txt
   ```

3. **Run ML Service:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## 🔧 Troubleshooting

### Package Installation Issues
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -v fastapi uvicorn

# Install specific versions
pip install fastapi==0.104.1 uvicorn==0.24.0
```

### Python Version Issues
```bash
# Check which Python is being used
where python
python --version

# Use specific Python version
py -3.9 -m pip install fastapi uvicorn
py -3.9 -m uvicorn app.main:app --reload --port 8000
```

### Permission Issues
```bash
# Install for user only
pip install --user fastapi uvicorn

# Or use --break-system-packages (not recommended)
pip install --break-system-packages fastapi uvicorn
```

## 🚀 Quick Test

Once packages are installed, test with:
```bash
cd ml-services
python test_server.py
```

This will verify all imports are working.

## 📝 Alternative: Run Without ML Service

If you can't get the ML service running, you can still test the frontend and backend:

1. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Start Backend:**
   ```bash
   cd backend
   npm install
   npm run dev
   ```

3. **Test Frontend:**
   - Go to http://localhost:3000
   - Try the interest selection feature
   - The resume upload will show an error (expected without ML service)

## 🎯 Why Python 3.9?

- ✅ **Better Package Compatibility** - Most ML packages support 3.9
- ✅ **Pre-compiled Wheels** - No compilation required
- ✅ **Stable Ecosystem** - Well-tested with all dependencies
- ✅ **Faster Installation** - No build tools needed

## 🆘 Still Having Issues?

1. **Use Python 3.9** - This solves most compatibility issues
2. **Check PATH** - Make sure Python is in your system PATH
3. **Use Virtual Environment** - Isolates your project dependencies
4. **Try Conda** - Often handles dependencies better than pip
5. **Check Antivirus** - Some antivirus software blocks pip installations

## 🎉 Success!

Once the ML service is running, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Happy coding! 🚀**
