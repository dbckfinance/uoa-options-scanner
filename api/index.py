"""
Vercel API entry point - redirects to Backend FastAPI app
"""
import sys
import os

# Add the Backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Backend'))

from main import app

# Export the FastAPI app for Vercel
def handler(request, context):
    """Vercel handler function"""
    return app(request, context)

# Make app available at module level for Vercel
app = app
