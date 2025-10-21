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
    
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get("PORT", 8000))
    
    # Disable reload in production (Render environment)
    reload = os.environ.get("RENDER") is None
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )
