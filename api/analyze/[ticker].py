"""
Vercel serverless function handler for options analysis
"""
import sys
import os
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple data models for the API response
class OptionContract:
    def __init__(self, contractSymbol, strike, type, expirationDate, lastPrice, 
                 volume, openInterest, volumeToOiRatio, premiumSpent, underlyingPrice,
                 moneyness="OTM", distanceFromStrike=0.0, unusualityLevel="UNUSUAL",
                 daysToExpiration=0, timeDecayRisk="MEDIUM", strategicSignal="OPTIONS FLOW"):
        self.contractSymbol = contractSymbol
        self.strike = strike
        self.type = type
        self.expirationDate = expirationDate
        self.lastPrice = lastPrice
        self.volume = volume
        self.openInterest = openInterest
        self.volumeToOiRatio = volumeToOiRatio
        self.premiumSpent = premiumSpent
        self.underlyingPrice = underlyingPrice
        self.moneyness = moneyness
        self.distanceFromStrike = distanceFromStrike
        self.unusualityLevel = unusualityLevel
        self.daysToExpiration = daysToExpiration
        self.timeDecayRisk = timeDecayRisk
        self.strategicSignal = strategicSignal

class MarketSentiment:
    def __init__(self, totalCallVolume, totalPutVolume, callPutRatio, 
                 bullishSignals, bearishSignals, netSentiment):
        self.totalCallVolume = totalCallVolume
        self.totalPutVolume = totalPutVolume
        self.callPutRatio = callPutRatio
        self.bullishSignals = bullishSignals
        self.bearishSignals = bearishSignals
        self.netSentiment = netSentiment

class DataQualityInfo:
    def __init__(self, data_source, last_updated, data_quality_score, warnings=None):
        self.data_source = data_source
        self.last_updated = last_updated
        self.data_quality_score = data_quality_score
        self.warnings = warnings or []

class UOAResponse:
    def __init__(self, ticker, analysisDate, underlyingPrice, totalContracts, 
                 unusualContracts, marketSentiment, topSignals, riskWarnings, dataQuality):
        self.ticker = ticker
        self.analysisDate = analysisDate
        self.underlyingPrice = underlyingPrice
        self.totalContracts = totalContracts
        self.unusualContracts = unusualContracts
        self.marketSentiment = marketSentiment
        self.topSignals = topSignals
        self.riskWarnings = riskWarnings
        self.dataQuality = dataQuality

def calculate_dte(expiration_date: str) -> int:
    """Calculate days to expiration."""
    try:
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
        today = datetime.now()
        return (exp_date - today).days
    except Exception:
        return 0

def get_options_data_yfinance(ticker_symbol: str) -> pd.DataFrame:
    """Get options data from yfinance"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        expirations = ticker.options[:8]  # Limit to first 8 expirations
        
        all_options = []
        
        for expiration in expirations:
            try:
                options_chain = ticker.option_chain(expiration)
                dte = calculate_dte(expiration)
                
                # Process calls
                if not options_chain.calls.empty:
                    calls = options_chain.calls.copy()
                    calls['type'] = 'call'
                    calls['expirationDate'] = expiration
                    calls['dte'] = dte
                    all_options.append(calls)
                
                # Process puts
                if not options_chain.puts.empty:
                    puts = options_chain.puts.copy()
                    puts['type'] = 'put'
                    puts['expirationDate'] = expiration
                    puts['dte'] = dte
                    all_options.append(puts)
                    
            except Exception as e:
                logger.warning(f"Error processing expiration {expiration}: {e}")
                continue
        
        if not all_options:
            raise Exception("No options data available from yfinance")
        
        return pd.concat(all_options, ignore_index=True)
    except Exception as e:
        logger.error(f"Error getting options data: {e}")
        raise e

def analyze_options_data(ticker_symbol: str, mode: str = "auto") -> UOAResponse:
    """Analyze unusual options activity for a given ticker"""
    try:
        ticker_symbol = ticker_symbol.upper()
        logger.info(f"🔍 Starting analysis for {ticker_symbol}")
        
        # Get current price
        logger.info(f"📈 Getting current price for {ticker_symbol}...")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
            
            price_data = yf.download(ticker_symbol, 
                                   start=start_date.strftime('%Y-%m-%d'), 
                                   end=end_date.strftime('%Y-%m-%d'), 
                                   progress=False)
            
            if price_data.empty:
                raise ValueError("No price data available")
                
            if 'Close' in price_data.columns:
                current_price = float(price_data['Close'].iloc[-1])
            elif isinstance(price_data.columns, pd.MultiIndex):
                close_cols = [col for col in price_data.columns if 'Close' in str(col)]
                if close_cols:
                    current_price = float(price_data[close_cols[0]].iloc[-1])
                else:
                    raise ValueError("No Close price found")
            else:
                raise ValueError("Unexpected data structure")
                
            logger.info(f"✅ Got current price: ${current_price:.2f} for {ticker_symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to get price for {ticker_symbol}: {e}")
            raise Exception(f"Could not fetch stock data for ticker '{ticker_symbol}'")
        
        # Get options data
        logger.info(f"📊 Getting options data for {ticker_symbol}...")
        try:
            combined_df = get_options_data_yfinance(ticker_symbol)
            
            if combined_df.empty:
                raise ValueError("No options data available")
            
            logger.info(f"✅ Retrieved {len(combined_df)} options contracts")
            
            # Calculate DTE if not present
            if 'dte' not in combined_df.columns:
                combined_df['dte'] = combined_df['expirationDate'].apply(calculate_dte)
            
            # Apply DTE filters (1-45 days)
            filtered_df = combined_df[
                (combined_df['dte'] >= 1) & 
                (combined_df['dte'] <= 45)
            ].copy()
            
            if filtered_df.empty:
                logger.info("No options data within DTE range 1-45 days")
                # Return empty response
                empty_sentiment = MarketSentiment(0, 0, 0.0, 0, 0, "NEUTRAL")
                data_quality = DataQualityInfo("Yahoo Finance", datetime.now().isoformat(), 75, ["No options within specified DTE range"])
                
                return UOAResponse(
                    ticker=ticker_symbol,
                    analysisDate=datetime.now().isoformat(),
                    underlyingPrice=current_price,
                    totalContracts=0,
                    unusualContracts=[],
                    marketSentiment=empty_sentiment,
                    topSignals=["No unusual options activity detected"],
                    riskWarnings=[],
                    dataQuality=data_quality
                )
            
            combined_df = filtered_df
            logger.info(f"After DTE filtering: {len(combined_df)} contracts")
            
        except Exception as e:
            logger.error(f"❌ Failed to get options data for {ticker_symbol}: {e}")
            raise Exception(f"Could not fetch options data for ticker '{ticker_symbol}'")
        
        # Clean and prepare data
        combined_df = combined_df.dropna(subset=['volume', 'openInterest', 'lastPrice'])
        combined_df = combined_df[combined_df['volume'] > 0]
        combined_df = combined_df[combined_df['openInterest'] > 0]
        
        # Calculate ratios and filters
        combined_df['volumeToOiRatio'] = combined_df['volume'] / combined_df['openInterest']
        combined_df['premiumSpent'] = combined_df['volume'] * combined_df['lastPrice'] * 100
        
        # Determine analysis mode
        total_volume = combined_df['volume'].sum()
        
        if mode == "live":
            has_volume = True
            logger.info(f"🔴 LIVE TRADING MODE: Using volume-based analysis")
        elif mode == "position":
            has_volume = False
            logger.info(f"🔵 POSITION ANALYSIS MODE: Using open interest-based analysis")
        else:  # mode == "auto"
            has_volume = total_volume > 1000
            logger.info(f"🤖 AUTO MODE: {'OPEN' if has_volume else 'CLOSED/PRE-MARKET'} (Total volume: {total_volume})")
        
        # Apply filters based on mode
        if has_volume:
            # Volume-based filters (LIVE TRADING)
            volume_filter = combined_df['volumeToOiRatio'] >= 1.0
            min_vol_filter = combined_df['volume'] >= 5
            min_oi_filter = combined_df['openInterest'] >= 10
            premium_filter = combined_df['premiumSpent'] >= 100.0
            
            unusual_options = combined_df[volume_filter & min_vol_filter & min_oi_filter & premium_filter].copy()
            unusual_options = unusual_options.sort_values('volumeToOiRatio', ascending=False)
            logger.info(f"✅ Found {len(unusual_options)} unusual contracts (volume-based)")
        else:
            # Position-based filters (POSITION ANALYSIS)
            combined_df['theoretical_premium'] = combined_df['openInterest'] * combined_df['lastPrice'] * 100
            
            oi_filter = combined_df['openInterest'] >= 20
            theoretical_premium_filter = combined_df['theoretical_premium'] >= 1000.0
            price_filter = combined_df['lastPrice'] > 0
            
            unusual_options = combined_df[oi_filter & theoretical_premium_filter & price_filter].copy()
            unusual_options = unusual_options.sort_values('openInterest', ascending=False)
            logger.info(f"✅ Found {len(unusual_options)} significant positions (open interest-based)")
        
        # Limit results
        unusual_options = unusual_options.head(100)
        
        # Convert to response format
        unusual_contracts = []
        for _, row in unusual_options.iterrows():
            try:
                if has_volume:
                    premium = float(row['premiumSpent'])
                    ratio = float(row['volumeToOiRatio'])
                else:
                    premium = float(row['theoretical_premium'])
                    ratio = 0.0
                
                contract = OptionContract(
                    contractSymbol=str(row['contractSymbol']),
                    strike=float(row['strike']),
                    type=str(row['type']),
                    expirationDate=str(row['expirationDate']),
                    lastPrice=float(row['lastPrice']),
                    volume=int(row['volume']),
                    openInterest=int(row['openInterest']),
                    volumeToOiRatio=ratio,
                    premiumSpent=premium,
                    underlyingPrice=float(current_price),
                    daysToExpiration=int(row['dte'])
                )
                unusual_contracts.append(contract)
            except Exception as e:
                logger.error(f"Error creating contract: {e}")
                continue
        
        # Calculate market sentiment
        call_volume = int(combined_df[combined_df['type'] == 'call']['volume'].sum()) if 'type' in combined_df.columns else 0
        put_volume = int(combined_df[combined_df['type'] == 'put']['volume'].sum()) if 'type' in combined_df.columns else 0
        call_put_ratio = call_volume / put_volume if put_volume > 0 else 1.0
        
        market_sentiment = MarketSentiment(
            totalCallVolume=call_volume,
            totalPutVolume=put_volume,
            callPutRatio=round(call_put_ratio, 2),
            bullishSignals=0,
            bearishSignals=0,
            netSentiment="NEUTRAL"
        )
        
        # Generate insights
        market_mode = "LIVE TRADING" if has_volume else "POSITION ANALYSIS"
        analysis_type = "Volume-based" if has_volume else "Open Interest-based"
        mode_icon = "🔴" if has_volume else "🔵"
        
        top_signals = [
            f"{mode_icon} {market_mode} MODE - {analysis_type} analysis",
            f"Found {len(unusual_contracts)} {'unusual contracts' if has_volume else 'significant positions'}",
            f"Data source: YAHOO FINANCE",
            f"Data quality: Good"
        ]
        
        if has_volume:
            top_signals.append("Filters: Vol/OI≥1.0, Vol≥5, Premium≥$100")
        else:
            top_signals.append("Filters: OI≥20, Premium≥$1000")
        
        risk_warnings = []
        
        # Create data quality info
        data_quality = DataQualityInfo(
            data_source="Yahoo Finance",
            last_updated=datetime.now().isoformat(),
            data_quality_score=75,
            warnings=[]
        )
        
        logger.info(f"✅ Analysis complete for {ticker_symbol}: {len(unusual_contracts)} contracts, {market_sentiment.netSentiment} sentiment")
        
        return UOAResponse(
            ticker=ticker_symbol,
            analysisDate=datetime.now().isoformat(),
            underlyingPrice=current_price,
            totalContracts=len(combined_df),
            unusualContracts=unusual_contracts,
            marketSentiment=market_sentiment,
            topSignals=top_signals,
            riskWarnings=risk_warnings,
            dataQuality=data_quality
        )
        
    except Exception as e:
        logger.error(f"Unexpected error analyzing {ticker_symbol}: {e}")
        raise Exception(f"Internal server error analyzing ticker '{ticker_symbol}': {str(e)}")

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
        
        # Simple test response first
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
            },
            'body': json.dumps({
                'ticker': ticker,
                'mode': mode,
                'message': 'API is working!',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
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
