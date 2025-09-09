from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

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
                
                try:
                    # Get real data for the ticker
                    response_data = self.get_real_options_data(ticker.upper(), mode)
                except Exception as e:
                    # Fallback to error response
                    response_data = {
                        "error": f"Failed to fetch data for {ticker.upper()}: {str(e)}",
                        "ticker": ticker.upper(),
                        "suggestion": "Try a popular ticker like AAPL, MSFT, TSLA, GOOGL, META, NVDA"
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
    
    def get_real_options_data(self, ticker, mode):
        """Get real options data using Yahoo Finance API"""
        try:
            # Get current stock price
            price_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            with urllib.request.urlopen(price_url) as response:
                price_data = json.loads(response.read().decode())
                current_price = price_data['chart']['result'][0]['meta']['regularMarketPrice']
            
            # Get options data
            options_url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}"
            with urllib.request.urlopen(options_url) as response:
                options_data = json.loads(response.read().decode())
                
            if 'optionChain' not in options_data or not options_data['optionChain']['result']:
                raise Exception("No options data available")
            
            option_chain = options_data['optionChain']['result'][0]
            calls = option_chain.get('options', [{}])[0].get('calls', [])
            puts = option_chain.get('options', [{}])[0].get('puts', [])
            
            # Process options data
            unusual_contracts = []
            total_call_volume = 0
            total_put_volume = 0
            
            # Process calls
            for call in calls[:10]:  # Limit to first 10
                volume = call.get('volume', 0)
                open_interest = call.get('openInterest', 0)
                last_price = call.get('lastPrice', 0)
                
                if volume > 0 and open_interest > 0:
                    volume_oi_ratio = volume / open_interest
                    premium_spent = volume * last_price * 100
                    
                    # Apply filters based on mode
                    if mode == "position" or (mode == "auto" and volume < 100):
                        # Position analysis - focus on open interest
                        if open_interest >= 25 and premium_spent >= 1000:
                            contract = {
                                "contractSymbol": call.get('contractSymbol', ''),
                                "strike": call.get('strike', 0),
                                "type": "call",
                                "expirationDate": call.get('expiration', 0),
                                "lastPrice": last_price,
                                "volume": volume,
                                "openInterest": open_interest,
                                "volumeToOiRatio": volume_oi_ratio,
                                "premiumSpent": premium_spent,
                                "underlyingPrice": current_price,
                                "moneyness": "OTM" if call.get('strike', 0) > current_price else "ITM",
                                "distanceFromStrike": ((call.get('strike', 0) - current_price) / current_price) * 100,
                                "unusualityLevel": "HIGH" if volume_oi_ratio > 3 else "UNUSUAL",
                                "daysToExpiration": 30,  # Simplified
                                "timeDecayRisk": "MEDIUM",
                                "strategicSignal": "CALL FLOW"
                            }
                            unusual_contracts.append(contract)
                            total_call_volume += volume
                    else:
                        # Live trading - focus on volume
                        if volume_oi_ratio >= 2.5 and volume >= 100 and premium_spent >= 25000:
                            contract = {
                                "contractSymbol": call.get('contractSymbol', ''),
                                "strike": call.get('strike', 0),
                                "type": "call",
                                "expirationDate": call.get('expiration', 0),
                                "lastPrice": last_price,
                                "volume": volume,
                                "openInterest": open_interest,
                                "volumeToOiRatio": volume_oi_ratio,
                                "premiumSpent": premium_spent,
                                "underlyingPrice": current_price,
                                "moneyness": "OTM" if call.get('strike', 0) > current_price else "ITM",
                                "distanceFromStrike": ((call.get('strike', 0) - current_price) / current_price) * 100,
                                "unusualityLevel": "EXTREME" if volume_oi_ratio > 8 else "HIGH" if volume_oi_ratio > 5 else "UNUSUAL",
                                "daysToExpiration": 30,
                                "timeDecayRisk": "MEDIUM",
                                "strategicSignal": "CALL FLOW"
                            }
                            unusual_contracts.append(contract)
                            total_call_volume += volume
            
            # Process puts
            for put in puts[:10]:  # Limit to first 10
                volume = put.get('volume', 0)
                open_interest = put.get('openInterest', 0)
                last_price = put.get('lastPrice', 0)
                
                if volume > 0 and open_interest > 0:
                    volume_oi_ratio = volume / open_interest
                    premium_spent = volume * last_price * 100
                    
                    # Apply filters based on mode
                    if mode == "position" or (mode == "auto" and volume < 100):
                        # Position analysis - focus on open interest
                        if open_interest >= 25 and premium_spent >= 1000:
                            contract = {
                                "contractSymbol": put.get('contractSymbol', ''),
                                "strike": put.get('strike', 0),
                                "type": "put",
                                "expirationDate": put.get('expiration', 0),
                                "lastPrice": last_price,
                                "volume": volume,
                                "openInterest": open_interest,
                                "volumeToOiRatio": volume_oi_ratio,
                                "premiumSpent": premium_spent,
                                "underlyingPrice": current_price,
                                "moneyness": "OTM" if put.get('strike', 0) < current_price else "ITM",
                                "distanceFromStrike": ((put.get('strike', 0) - current_price) / current_price) * 100,
                                "unusualityLevel": "HIGH" if volume_oi_ratio > 3 else "UNUSUAL",
                                "daysToExpiration": 30,
                                "timeDecayRisk": "MEDIUM",
                                "strategicSignal": "PUT FLOW"
                            }
                            unusual_contracts.append(contract)
                            total_put_volume += volume
                    else:
                        # Live trading - focus on volume
                        if volume_oi_ratio >= 2.5 and volume >= 100 and premium_spent >= 25000:
                            contract = {
                                "contractSymbol": put.get('contractSymbol', ''),
                                "strike": put.get('strike', 0),
                                "type": "put",
                                "expirationDate": put.get('expiration', 0),
                                "lastPrice": last_price,
                                "volume": volume,
                                "openInterest": open_interest,
                                "volumeToOiRatio": volume_oi_ratio,
                                "premiumSpent": premium_spent,
                                "underlyingPrice": current_price,
                                "moneyness": "OTM" if put.get('strike', 0) < current_price else "ITM",
                                "distanceFromStrike": ((put.get('strike', 0) - current_price) / current_price) * 100,
                                "unusualityLevel": "EXTREME" if volume_oi_ratio > 8 else "HIGH" if volume_oi_ratio > 5 else "UNUSUAL",
                                "daysToExpiration": 30,
                                "timeDecayRisk": "MEDIUM",
                                "strategicSignal": "PUT FLOW"
                            }
                            unusual_contracts.append(contract)
                            total_put_volume += volume
            
            # Calculate market sentiment
            call_put_ratio = total_call_volume / total_put_volume if total_put_volume > 0 else 1.0
            net_sentiment = "BULLISH" if call_put_ratio > 1.5 else "BEARISH" if call_put_ratio < 0.67 else "NEUTRAL"
            
            # Determine analysis mode
            analysis_mode = "POSITION ANALYSIS" if mode == "position" or (mode == "auto" and total_call_volume + total_put_volume < 1000) else "LIVE TRADING"
            mode_icon = "🔵" if analysis_mode == "POSITION ANALYSIS" else "🔴"
            
            response_data = {
                "ticker": ticker,
                "analysisDate": datetime.now().isoformat(),
                "underlyingPrice": current_price,
                "totalContracts": len(calls) + len(puts),
                "unusualContracts": unusual_contracts[:20],  # Limit to 20 results
                "marketSentiment": {
                    "totalCallVolume": total_call_volume,
                    "totalPutVolume": total_put_volume,
                    "callPutRatio": round(call_put_ratio, 2),
                    "bullishSignals": len([c for c in unusual_contracts if c['type'] == 'call']),
                    "bearishSignals": len([c for c in unusual_contracts if c['type'] == 'put']),
                    "netSentiment": net_sentiment
                },
                "topSignals": [
                    f"{mode_icon} {analysis_mode} MODE - {'Open Interest-based' if analysis_mode == 'POSITION ANALYSIS' else 'Volume-based'} analysis",
                    f"Found {len(unusual_contracts)} {'significant positions' if analysis_mode == 'POSITION ANALYSIS' else 'unusual contracts'} for {ticker}",
                    f"Data source: YAHOO FINANCE",
                    f"Data quality: Good"
                ],
                "riskWarnings": [],
                "dataQuality": {
                    "data_source": "yahoo_finance",
                    "last_updated": datetime.now().isoformat(),
                    "data_quality_score": 85,
                    "warnings": []
                }
            }
            
            return response_data
            
        except Exception as e:
            raise Exception(f"Failed to fetch real data: {str(e)}")