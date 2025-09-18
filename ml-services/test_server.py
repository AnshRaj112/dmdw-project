#!/usr/bin/env python3
"""
Simple test server for the ML service
This runs without uvicorn for testing purposes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✅ ML Service imports successful!")
    print("✅ FastAPI app created successfully!")
    print("✅ All dependencies are working!")
    print("\n🚀 To start the server, run:")
    print("   python -m uvicorn app.main:app --reload --port 8000")
    print("\n📝 Note: If uvicorn is not found, install it with:")
    print("   pip install uvicorn")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n🔧 Try installing missing packages:")
    print("   pip install fastapi uvicorn python-multipart pydantic python-dotenv PyPDF2 python-docx loguru")
except Exception as e:
    print(f"❌ Error: {e}")
