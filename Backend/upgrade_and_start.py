#!/usr/bin/env python3
"""
Script to upgrade yfinance and start the UOA backend server
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 UOA Backend Upgrade and Startup Script")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not sys.prefix != sys.base_prefix:
        print("⚠️  Warning: Not in a virtual environment!")
        print("Please activate your virtual environment first:")
        print("venv\\Scripts\\activate")
        return
    
    # Upgrade yfinance to the working version
    if not run_command("pip install yfinance==0.2.61", "Upgrading yfinance to v0.2.61"):
        return
    
    # Install any missing dependencies
    if not run_command("pip install -r requirements.txt", "Installing/updating all dependencies"):
        return
    
    print("\n" + "=" * 50)
    print("🎯 Starting UOA Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    try:
        from main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
