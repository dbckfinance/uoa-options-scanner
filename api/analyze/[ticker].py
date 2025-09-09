import json
from datetime import datetime

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
        
        if not ticker:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
                },
                'body': json.dumps({'detail': 'Ticker parameter is required'})
            }
        
        # Simple test response
        response_data = {
            'ticker': ticker,
            'mode': mode,
            'message': 'API is working!',
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
            },
            'body': json.dumps(response_data)
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
            'body': json.dumps({'detail': f'An error occurred: {str(e)}'})
        }
