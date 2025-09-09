"""
Vercel serverless function handler for options analysis
"""
import sys
import os

# Add Backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Backend'))

from Backend.main import app
from fastapi import Request
import json

def handler(request, event, context):
    """Vercel serverless function handler"""
    try:
        # Handle CORS preflight requests
        if request.get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        
        # Extract ticker from path
        ticker = event.get('params', {}).get('ticker', '')
        
        # Extract query parameters
        query_params = event.get('query', {})
        mode = query_params.get('mode', 'auto')
        
        # Create a mock request for FastAPI
        class MockRequest:
            def __init__(self, method="GET", url="/", headers={}):
                self.method = method
                self.url = url
                self.headers = headers
        
        # Call the FastAPI app with mode parameter
        response = app.get(f"/api/analyze/{ticker}?mode={mode}")
        return {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
            },
            'body': json.dumps(response.json())
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
            },
            'body': json.dumps({'detail': str(e)})
        }
