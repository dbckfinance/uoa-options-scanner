"""
Vercel serverless function entry point for FastAPI
"""
from main import app

# Export the FastAPI app for Vercel
def handler(request, context):
    """Vercel handler function"""
    return app(request, context)

# Make app available at module level for Vercel
app = app
