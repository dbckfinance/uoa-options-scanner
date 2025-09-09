from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract ticker from path
            path_parts = self.path.split('/')
            ticker = path_parts[-1] if path_parts else ''
            
            # Extract query parameters
            if '?' in self.path:
                query_string = self.path.split('?')[1]
                mode = 'auto'
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        if key == 'mode':
                            mode = value
            else:
                mode = 'auto'
            
            if not ticker:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'detail': 'Ticker parameter is required'}).encode())
                return
            
            # Simple test response
            response_data = {
                'ticker': ticker,
                'mode': mode,
                'message': 'API is working!',
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': f'An error occurred: {str(e)}'}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
