#!/usr/bin/env python3
"""
Simple script to start the UOA backend server - SIMPLIFIED APPROACH
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 UOA Backend Server - SIMPLE APPROACH")
    print("📍 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    print("-" * 40)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
