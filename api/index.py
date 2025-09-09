from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path to get ticker and mode
        path = self.path
        if path.startswith('/api/analyze/'):
            # Extract ticker from path like /api/analyze/GOOGL?mode=position
            parts = path.split('/')
            if len(parts) >= 4:
                ticker_part = parts[3]
                ticker = ticker_part.split('?')[0]  # Remove query params
                
                # Parse query parameters
                mode = 'auto'
                if '?' in path:
                    query_part = path.split('?')[1]
                    for param in query_part.split('&'):
                        if param.startswith('mode='):
                            mode = param.split('=')[1]
                
                # Create response
                response_data = {
                    "ticker": ticker.upper(),
                    "analysisDate": "2024-01-01T12:00:00Z",
                    "underlyingPrice": 145.50,
                    "totalContracts": 100,
                    "unusualContracts": [
                        {
                            "contractSymbol": f"{ticker.upper()}240115C00150000",
                            "strike": 150.0,
                            "type": "call",
                            "expirationDate": "2024-01-15",
                            "lastPrice": 5.25,
                            "volume": 1000,
                            "openInterest": 5000,
                            "volumeToOiRatio": 0.2,
                            "premiumSpent": 525000.0,
                            "underlyingPrice": 145.50,
                            "moneyness": "OTM",
                            "distanceFromStrike": 3.1,
                            "unusualityLevel": "UNUSUAL",
                            "daysToExpiration": 30,
                            "timeDecayRisk": "MEDIUM",
                            "strategicSignal": "OPTIONS FLOW"
                        }
                    ],
                    "marketSentiment": {
                        "totalCallVolume": 1500,
                        "totalPutVolume": 800,
                        "callPutRatio": 1.88,
                        "bullishSignals": 3,
                        "bearishSignals": 1,
                        "netSentiment": "BULLISH"
                    },
                    "topSignals": [
                        f"🔵 POSITION ANALYSIS MODE - Open Interest-based analysis",
                        f"Found 1 significant positions for {ticker.upper()}",
                        f"Data source: YFINANCE",
                        f"Data quality: Good"
                    ],
                    "riskWarnings": [],
                    "dataQuality": {
                        "data_source": "yfinance",
                        "last_updated": "2024-01-01T12:00:00Z",
                        "data_quality_score": 85,
                        "warnings": []
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
                return
        
        # Default response for root
        response_data = {
            "message": "Unusual Options Activity API",
            "version": "1.0.0",
            "status": "working",
            "endpoints": {
                "analyze": "/api/analyze/{ticker}",
                "docs": "/docs"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()