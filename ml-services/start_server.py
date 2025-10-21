#!/usr/bin/env python3
"""
Startup script for ML Services
Handles Python path setup for uvicorn
"""
import os
import sys
import subprocess

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = current_dir

if __name__ == "__main__":
    # Import and run uvicorn
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True
    )
