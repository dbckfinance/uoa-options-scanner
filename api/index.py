"""
Vercel API entry point - redirects to Backend FastAPI app
"""
import sys
import os
from mangum import Mangum

# Add the Backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Backend'))

from main import app

# Create ASGI handler for Vercel
handler = Mangum(app)
