from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
import configparser
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import time
from models import OptionContract, UOAResponse, ErrorResponse, MarketSentiment, DataSource, IBKRConnectionStatus, IBKRDataMetrics, DataQualityInfo
from ibkr_client import IBKRClient

# Simple, direct approach like the working correlation app - no custom sessions or headers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Unusual Options Activity API",
    description="API for analyzing unusual options activity for US stock tickers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "https://uoa-options-scanner.vercel.app",
        "https://uoa-options-scanner-*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Get filtering parameters from config
MIN_VOL_OI_RATIO = float(config.get('FILTERING', 'min_volume_oi_ratio', fallback=1.0))
MIN_VOLUME = int(config.get('FILTERING', 'min_volume', fallback=50))
MIN_OPEN_INTEREST = int(config.get('FILTERING', 'min_open_interest', fallback=10))
MAX_DTE = int(config.get('FILTERING', 'max_dte', fallback=45))
MIN_DTE = int(config.get('FILTERING', 'min_dte', fallback=1))
MIN_PREMIUM_SPENT = float(config.get('FILTERING', 'min_premium_spent', fallback=1000.0))
MAX_RESULTS = int(config.get('FILTERING', 'max_results', fallback=100))

# Different thresholds for different modes
LIVE_TRADING_MIN_PREMIUM = 100.0  # Lower threshold for live trading
POSITION_ANALYSIS_MIN_PREMIUM = 1000.0  # Higher threshold for position analysis
LIVE_TRADING_MIN_VOLUME = 5  # Lower volume threshold for live trading
POSITION_ANALYSIS_MIN_OI = 20  # Higher OI threshold for position analysis

# IBKR configuration
ENABLE_IBKR = config.getboolean('IBKR_CONNECTION', 'enable_ibkr') if config.has_option('IBKR_CONNECTION', 'enable_ibkr') else False
USE_IBKR_PRIMARY = config.getboolean('IBKR_CONNECTION', 'use_ibkr_primary') if config.has_option('IBKR_CONNECTION', 'use_ibkr_primary') else False
FALLBACK_TO_YFINANCE = config.getboolean('IBKR_CONNECTION', 'fallback_to_yfinance') if config.has_option('IBKR_CONNECTION', 'fallback_to_yfinance') else True
FALLBACK_TIMEOUT = int(config.get('IBKR_CONNECTION', 'fallback_timeout')) if config.has_option('IBKR_CONNECTION', 'fallback_timeout') else 5

# Initialize IBKR client (global instance)
ibkr_client: Optional[IBKRClient] = None
ibkr_connection_status: IBKRConnectionStatus = IBKRConnectionStatus(connected=False)

def initialize_ibkr_client():
    """Initialize IBKR client if enabled"""
    global ibkr_client, ibkr_connection_status
    
    if not ENABLE_IBKR:
        logger.info("IBKR disabled in configuration")
        return
    
    try:
        logger.info("Initializing IBKR client...")
        ibkr_client = IBKRClient('config.ini')
        ibkr_connection_status = ibkr_client.connect_to_ibkr()
        
        if ibkr_connection_status.connected:
            logger.info("✅ IBKR client initialized and connected successfully")
        else:
            logger.warning(f"⚠️ IBKR connection failed: {ibkr_connection_status.error_message}")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize IBKR client: {e}")
        ibkr_connection_status = IBKRConnectionStatus(
            connected=False,
            error_message=str(e)
        )

# Initialize IBKR on startup (only if enabled)
if ENABLE_IBKR:
    initialize_ibkr_client()
else:
    logger.info("IBKR disabled - using yfinance only")

def calculate_dte(expiration_date: str) -> int:
    """Calculate days to expiration."""
    try:
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
        today = datetime.now()
        return (exp_date - today).days
    except Exception:
        return 0

# Simple approach like the working correlation app - no custom sessions or headers

def calculate_moneyness(strike: float, underlying_price: float, option_type: str) -> tuple[str, float]:
    """Calculate moneyness and distance from strike (EXPERT ANALYSIS)."""
    distance = (strike - underlying_price) / underlying_price
    abs_distance = abs(distance)
    
    # ATM threshold from config
    atm_threshold = float(config.get('EXPERT_ANALYSIS', 'atm_threshold', fallback=0.05))
    deep_threshold = float(config.get('EXPERT_ANALYSIS', 'deep_otm_threshold', fallback=0.15))
    
    if abs_distance <= atm_threshold:
        moneyness = "ATM"
    elif option_type.lower() == 'call':
        if distance < 0:  # Strike below current price
            moneyness = "ITM"
        elif distance > deep_threshold:
            moneyness = "Deep-OTM"
        else:
            moneyness = "OTM"
    else:  # put
        if distance > 0:  # Strike above current price
            moneyness = "ITM" 
        elif abs_distance > deep_threshold:
            moneyness = "Deep-OTM"
        else:
            moneyness = "OTM"
    
    return moneyness, distance * 100  # Return as percentage

def determine_unusuality_level(ratio: float) -> str:
    """Classify unusuality level based on Volume/OI ratio (EXPERT ANALYSIS)."""
    high_ratio = float(config.get('EXPERT_ANALYSIS', 'high_unusual_ratio', fallback=5.0))
    extreme_ratio = float(config.get('EXPERT_ANALYSIS', 'extreme_unusual_ratio', fallback=8.0))
    
    if ratio >= extreme_ratio:
        return "EXTREME"
    elif ratio >= high_ratio:
        return "HIGH"
    else:
        return "UNUSUAL"

def validate_data_quality(df: pd.DataFrame, ticker: str) -> tuple[bool, list[str]]:
    """
    Validate data quality and consistency.
    Returns (is_valid, list_of_warnings)
    """
    warnings = []
    is_valid = True
    
    # Check for missing data
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        warnings.append(f"Missing data detected: {missing_data.sum()} null values")
        is_valid = False
    
    # Check for unrealistic values
    if 'volume' in df.columns:
        # Volume should be positive integers
        invalid_volume = df[df['volume'] <= 0]
        if len(invalid_volume) > 0:
            warnings.append(f"Invalid volume data: {len(invalid_volume)} contracts with volume <= 0")
            is_valid = False
    
    if 'openInterest' in df.columns:
        # Open interest should be positive integers
        invalid_oi = df[df['openInterest'] <= 0]
        if len(invalid_oi) > 0:
            warnings.append(f"Invalid open interest data: {len(invalid_oi)} contracts with OI <= 0")
            is_valid = False
    
    if 'lastPrice' in df.columns:
        # Price should be positive and reasonable
        invalid_price = df[df['lastPrice'] <= 0]
        if len(invalid_price) > 0:
            warnings.append(f"Invalid price data: {len(invalid_price)} contracts with price <= 0")
            is_valid = False
    
    # Check for data freshness (if timestamp available)
    if 'lastTradeDate' in df.columns:
        try:
            # Check if data is not too old (within last 24 hours)
            current_time = datetime.now()
            for date_str in df['lastTradeDate'].dropna():
                try:
                    trade_date = pd.to_datetime(date_str)
                    if (current_time - trade_date).days > 1:
                        warnings.append("Some data may be stale (older than 24 hours)")
                        break
                except:
                    continue
        except:
            pass
    
    # Check for reasonable volume/OI ratios
    if 'volume' in df.columns and 'openInterest' in df.columns:
        df_temp = df.copy()
        df_temp['vol_oi_ratio'] = df_temp['volume'] / df_temp['openInterest']
        extreme_ratios = df_temp[df_temp['vol_oi_ratio'] > 100]  # Suspicious ratios
        if len(extreme_ratios) > 0:
            warnings.append(f"Extreme volume/OI ratios detected: {len(extreme_ratios)} contracts with ratio > 100x")
            # Don't mark as invalid, just warn
    
    return is_valid, warnings

def cross_validate_price_data(ticker_symbol: str, options_price: float, underlying_price: float) -> tuple[bool, str]:
    """
    Cross-validate price data for consistency.
    Returns (is_valid, warning_message)
    """
    try:
        # Get additional price data for validation
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Check if underlying price is reasonable
        if 'regularMarketPrice' in info and info['regularMarketPrice']:
            market_price = info['regularMarketPrice']
            price_diff = abs(underlying_price - market_price) / market_price
            
            if price_diff > 0.05:  # 5% difference threshold
                return False, f"Price discrepancy detected: API price ${underlying_price:.2f} vs Market price ${market_price:.2f}"
        
        # Check if options price is reasonable relative to underlying
        if options_price > underlying_price * 0.5:  # Options shouldn't cost more than 50% of underlying
            return False, f"Options price ${options_price:.2f} seems unrealistic relative to underlying price ${underlying_price:.2f}"
        
        return True, ""
        
    except Exception as e:
        logger.warning(f"Cross-validation failed: {e}")
        return True, ""  # Don't fail on validation errors

def get_options_data_ibkr(ticker_symbol: str) -> pd.DataFrame:
    """
    Get options data from IBKR
    """
    global ibkr_client, ibkr_connection_status
    
    if not ibkr_client or not ibkr_connection_status.connected:
        raise Exception("IBKR not connected")
    
    try:
        logger.info(f"📊 Getting options data from IBKR for {ticker_symbol}")
        options_df = ibkr_client.get_options_chain(ticker_symbol)
        
        if options_df.empty:
            raise Exception("No options data returned from IBKR")
        
        # Add IBKR-specific fields
        options_df['dataSource'] = DataSource.IBKR
        options_df['dataQuality'] = 95  # High quality for IBKR
        
        logger.info(f"✅ Retrieved {len(options_df)} options contracts from IBKR")
        return options_df
        
    except Exception as e:
        logger.error(f"❌ IBKR data retrieval failed: {e}")
        raise e

def get_options_data_hybrid(ticker_symbol: str) -> tuple[pd.DataFrame, DataSource, dict]:
    """
    Get options data using hybrid approach: IBKR primary, yfinance fallback
    Returns: (dataframe, data_source, quality_info)
    """
    quality_info = {
        "attempted_sources": [],
        "successful_source": None,
        "fallback_used": False,
        "errors": []
    }
    
    # Try IBKR first if enabled and connected
    if USE_IBKR_PRIMARY and ibkr_client and ibkr_connection_status.connected:
        try:
            quality_info["attempted_sources"].append("IBKR")
            options_df = get_options_data_ibkr(ticker_symbol)
            quality_info["successful_source"] = DataSource.IBKR
            return options_df, DataSource.IBKR, quality_info
            
        except Exception as e:
            error_msg = f"IBKR failed: {e}"
            logger.warning(error_msg)
            quality_info["errors"].append(error_msg)
            
            if not FALLBACK_TO_YFINANCE:
                raise Exception(f"IBKR failed and fallback disabled: {e}")
    
    # Fallback to yfinance
    if FALLBACK_TO_YFINANCE:
        try:
            quality_info["attempted_sources"].append("yfinance")
            quality_info["fallback_used"] = True
            
            logger.info(f"📈 Using yfinance fallback for {ticker_symbol}")
            options_df = get_options_data_yfinance(ticker_symbol)
            quality_info["successful_source"] = DataSource.YFINANCE
            
            return options_df, DataSource.YFINANCE, quality_info
            
        except Exception as e:
            error_msg = f"yfinance fallback failed: {e}"
            logger.error(error_msg)
            quality_info["errors"].append(error_msg)
            raise Exception(f"All data sources failed: {quality_info['errors']}")
    
    raise Exception("No data sources available")

def get_options_data_yfinance(ticker_symbol: str) -> pd.DataFrame:
    """
    Get options data from yfinance (existing implementation)
    """
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
                calls['dataSource'] = DataSource.YFINANCE
                calls['dataQuality'] = 75  # Good quality for yfinance
                all_options.append(calls)
            
            # Process puts
            if not options_chain.puts.empty:
                puts = options_chain.puts.copy()
                puts['type'] = 'put'
                puts['expirationDate'] = expiration
                puts['dte'] = dte
                puts['dataSource'] = DataSource.YFINANCE
                puts['dataQuality'] = 75  # Good quality for yfinance
                all_options.append(puts)
                
        except Exception as e:
            logger.warning(f"Error processing expiration {expiration}: {e}")
            continue
    
    if not all_options:
        raise Exception("No options data available from yfinance")
    
    return pd.concat(all_options, ignore_index=True)

def get_data_freshness_info(ticker_symbol: str) -> dict:
    """
    Get information about data freshness and reliability.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        freshness_info = {
            "data_source": "Yahoo Finance",
            "last_updated": datetime.now().isoformat(),
            "exchange": info.get('exchange', 'Unknown'),
            "market_cap": info.get('marketCap', 0),
            "volume_24h": info.get('volume', 0),
            "data_quality_score": 0
        }
        
        # Calculate data quality score
        score = 100
        
        # Deduct points for missing critical data
        if not info.get('regularMarketPrice'):
            score -= 20
        if not info.get('volume'):
            score -= 15
        if not info.get('marketCap'):
            score -= 10
            
        freshness_info["data_quality_score"] = max(0, score)
        
        return freshness_info
        
    except Exception as e:
        logger.warning(f"Could not get freshness info: {e}")
        return {
            "data_source": "Yahoo Finance",
            "last_updated": datetime.now().isoformat(),
            "data_quality_score": 50
        }

def assess_time_decay_risk(dte: int) -> str:
    """Assess time decay risk based on days to expiration (EXPERT ANALYSIS)."""
    if dte <= 7:
        return "HIGH"
    elif dte <= 21:
        return "MEDIUM"
    else:
        return "LOW"

def generate_strategic_signal(moneyness: str, option_type: str, ratio: float, dte: int, premium: float) -> str:
    """Generate strategic trading signal interpretation (EXPERT ANALYSIS)."""
    signals = []
    
    # High premium + High ratio = Smart money
    if premium >= 100000 and ratio >= 6.0:
        signals.append("🔥 SMART MONEY")
    
    # Moneyness-based signals
    if moneyness == "ATM" and dte <= 14:
        signals.append("🎯 GAMMA SQUEEZE SETUP")
    elif moneyness == "Deep-OTM" and ratio >= 8.0:
        signals.append("🚀 LOTTERY TICKET PLAY")
    elif moneyness == "ITM" and premium >= 50000:
        signals.append("💪 CONVICTION TRADE")
    
    # Type-based signals
    if option_type.lower() == 'call':
        if dte <= 7 and ratio >= 5.0:
            signals.append("⚡ SHORT-TERM BULLISH")
        elif dte >= 30:
            signals.append("📈 LONG-TERM BULLISH")
    else:  # put
        if dte <= 7 and ratio >= 5.0:
            signals.append("⚡ SHORT-TERM BEARISH")
        elif dte >= 30:
            signals.append("📉 LONG-TERM BEARISH")
    
    return " | ".join(signals) if signals else f"{option_type.upper()} FLOW"

def calculate_market_sentiment(df: pd.DataFrame) -> MarketSentiment:
    """Calculate market sentiment from options flow (EXPERT ANALYSIS)."""
    call_volume = int(df[df['type'] == 'call']['volume'].sum())
    put_volume = int(df[df['type'] == 'put']['volume'].sum())
    
    total_volume = call_volume + put_volume
    call_put_ratio = call_volume / put_volume if put_volume > 0 else float('inf')
    
    # Count bullish/bearish signals
    bullish_signals = len(df[(df['type'] == 'call') & (df['volumeToOiRatio'] >= 3.0)])
    bearish_signals = len(df[(df['type'] == 'put') & (df['volumeToOiRatio'] >= 3.0)])
    
    # Determine net sentiment
    if call_put_ratio > 1.5:
        net_sentiment = "BULLISH"
    elif call_put_ratio < 0.67:
        net_sentiment = "BEARISH"
    else:
        net_sentiment = "NEUTRAL"
    
    return MarketSentiment(
        totalCallVolume=call_volume,
        totalPutVolume=put_volume,
        callPutRatio=round(call_put_ratio, 2),
        bullishSignals=bullish_signals,
        bearishSignals=bearish_signals,
        netSentiment=net_sentiment
    )

def generate_expert_insights(df: pd.DataFrame, sentiment: MarketSentiment) -> tuple[List[str], List[str]]:
    """Generate expert trading insights and risk warnings."""
    insights = []
    warnings = []
    
    # Top insights
    if sentiment.callPutRatio > 2.0:
        insights.append(f"🚀 Strong bullish sentiment: {sentiment.callPutRatio:.1f}x more call volume")
    elif sentiment.callPutRatio < 0.5:
        insights.append(f"🐻 Strong bearish sentiment: {sentiment.callPutRatio:.1f}x call/put ratio")
    
    extreme_flows = df[df['volumeToOiRatio'] >= 8.0]
    if not extreme_flows.empty:
        insights.append(f"🔥 {len(extreme_flows)} EXTREME flows detected (8x+ volume/OI)")
    
    # Smart money detection
    big_premium = df[df['premiumSpent'] >= 100000]
    if not big_premium.empty:
        insights.append(f"💰 {len(big_premium)} high-conviction trades (>$100K premium)")
    
    # Risk warnings
    short_dte = df[df['dte'] <= 7]
    if not short_dte.empty:
        warnings.append(f"⚠️ {len(short_dte)} contracts expire within 7 days (HIGH time decay)")
    
    deep_otm = len([r for _, r in df.iterrows() if 'Deep-OTM' in str(r.get('moneyness', ''))])
    if deep_otm > 0:
        warnings.append(f"🎲 {deep_otm} deep OTM positions detected (lottery ticket plays)")
    
    return insights[:5], warnings[:3]  # Limit to most important

def analyze_options_data(ticker_symbol: str, mode: str = "auto") -> UOAResponse:
    """Analyze unusual options activity for a given ticker - SIMPLE APPROACH like working correlation app."""
    try:
        ticker_symbol = ticker_symbol.upper()
        logger.info(f"🔍 Starting analysis for {ticker_symbol}")
        
        # Method 1: Get current price using yf.download (same approach as working correlation app)
        logger.info(f"📈 Getting current price for {ticker_symbol} using yf.download...")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)  # Get last 5 days
            
            price_data = yf.download(ticker_symbol, 
                                   start=start_date.strftime('%Y-%m-%d'), 
                                   end=end_date.strftime('%Y-%m-%d'), 
                                   progress=False)
            
            if price_data.empty:
                raise ValueError("No price data available")
                
            # Get Close price (same logic as correlation app)
            if 'Close' in price_data.columns:
                current_price = float(price_data['Close'].iloc[-1])
            elif isinstance(price_data.columns, pd.MultiIndex):
                # Handle multi-index columns
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
            suggested_tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "GOOGL"]
            suggestions = ", ".join([t for t in suggested_tickers if t != ticker_symbol][:5])
            raise HTTPException(
                status_code=404, 
                detail=f"Could not fetch stock data for ticker '{ticker_symbol}'. Try these popular tickers instead: {suggestions}"
            )
        
        # Method 2: Get options data using yfinance only (IBKR disabled on Vercel)
        logger.info(f"📊 Getting options data for {ticker_symbol} using yfinance...")
        try:
            # Use yfinance directly since IBKR is disabled
            combined_df = get_options_data_yfinance(ticker_symbol)
            data_source = DataSource.YFINANCE
            quality_info = {
                "attempted_sources": ["yfinance"],
                "successful_source": DataSource.YFINANCE,
                "fallback_used": False,
                "errors": []
            }
            
            if combined_df.empty:
                raise ValueError("No options data available from any source")
            
            logger.info(f"✅ Retrieved {len(combined_df)} options contracts from {data_source.value}")
            
            # Filter by DTE if needed (IBKR may have already filtered)
            if 'dte' not in combined_df.columns:
                # Calculate DTE if not present
                combined_df['dte'] = combined_df['expirationDate'].apply(calculate_dte)
            
            # Apply DTE filters
            filtered_df = combined_df[
                (combined_df['dte'] >= MIN_DTE) & 
                (combined_df['dte'] <= MAX_DTE)
            ].copy()
            
            if filtered_df.empty:
                logger.info(f"No options data within DTE range {MIN_DTE}-{MAX_DTE} days")
                # Return empty response
                empty_sentiment = MarketSentiment(
                    totalCallVolume=0,
                    totalPutVolume=0,
                    callPutRatio=0.0,
                    bullishSignals=0,
                    bearishSignals=0,
                    netSentiment="NEUTRAL"
                )
                
                # Create data quality info
                data_quality = DataQualityInfo(
                    data_source=data_source,
                    last_updated=datetime.now().isoformat(),
                    data_quality_score=85 if data_source == DataSource.IBKR else 75,
                    warnings=["No options within specified DTE range"]
                )
                
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
            suggested_tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "GOOGL"]
            suggestions = ", ".join([t for t in suggested_tickers if t != ticker_symbol][:5])
            raise HTTPException(
                status_code=404, 
                detail=f"Could not fetch options data for ticker '{ticker_symbol}'. Sources tried: {quality_info.get('attempted_sources', 'unknown')}. Try these popular tickers instead: {suggestions}"
            )
        
        # Clean and prepare data
        combined_df = combined_df.dropna(subset=['volume', 'openInterest', 'lastPrice'])
        combined_df = combined_df[combined_df['volume'] > 0]
        combined_df = combined_df[combined_df['openInterest'] > 0]
        
        # Calculate ratios and filters
        combined_df['volumeToOiRatio'] = combined_df['volume'] / combined_df['openInterest']
        combined_df['premiumSpent'] = combined_df['volume'] * combined_df['lastPrice'] * 100
        
        # Apply filters for unusual activity
        logger.info(f"Applying filters to {len(combined_df)} total contracts...")
        
        # Determine analysis mode based on parameter and market conditions
        total_volume = combined_df['volume'].sum()
        
        if mode == "live":
            has_volume = True
            logger.info(f"🔴 LIVE TRADING MODE: Using volume-based analysis")
            logger.info(f"  - Forced LIVE mode regardless of market status")
        elif mode == "position":
            has_volume = False
            logger.info(f"🔵 POSITION ANALYSIS MODE: Using open interest-based analysis")
            logger.info(f"  - Forced POSITION mode regardless of market status")
        else:  # mode == "auto"
            # Auto-detect based on volume activity
            has_volume = total_volume > 1000  # Threshold for significant volume
            logger.info(f"🤖 AUTO MODE: {'OPEN' if has_volume else 'CLOSED/PRE-MARKET'} (Total volume: {total_volume})")
        
        logger.info(f"Final mode decision: {'LIVE TRADING' if has_volume else 'POSITION ANALYSIS'} (Total volume: {total_volume})")
        
        if has_volume:
            # Market is open - use volume-based filters (LIVE TRADING)
            logger.info(f"🔴 LIVE TRADING FILTERS:")
            logger.info(f"  - Volume/OI Ratio >= {MIN_VOL_OI_RATIO}")
            logger.info(f"  - Volume >= {LIVE_TRADING_MIN_VOLUME}")
            logger.info(f"  - Open Interest >= {MIN_OPEN_INTEREST}")
            logger.info(f"  - Premium Spent >= ${LIVE_TRADING_MIN_PREMIUM:,.0f}")
            
            # Apply volume-based filters with LIVE TRADING thresholds
            volume_filter = combined_df['volumeToOiRatio'] >= MIN_VOL_OI_RATIO
            min_vol_filter = combined_df['volume'] >= LIVE_TRADING_MIN_VOLUME
            min_oi_filter = combined_df['openInterest'] >= MIN_OPEN_INTEREST
            premium_filter = combined_df['premiumSpent'] >= LIVE_TRADING_MIN_PREMIUM
            
            logger.info(f"  - Volume/OI filter: {volume_filter.sum()} contracts")
            logger.info(f"  - Min volume filter: {min_vol_filter.sum()} contracts")
            logger.info(f"  - Min OI filter: {min_oi_filter.sum()} contracts")
            logger.info(f"  - Premium filter: {premium_filter.sum()} contracts")
            
            unusual_options = combined_df[volume_filter & min_vol_filter & min_oi_filter & premium_filter].copy()
            logger.info(f"✅ Found {len(unusual_options)} unusual contracts (volume-based)")
        else:
            # Market is closed - analyze existing positions by open interest (POSITION ANALYSIS)
            logger.info("🔵 POSITION ANALYSIS FILTERS:")
            logger.info(f"  - Open Interest >= {POSITION_ANALYSIS_MIN_OI}")
            logger.info(f"  - Theoretical Premium >= ${POSITION_ANALYSIS_MIN_PREMIUM:,.0f}")
            logger.info(f"  - Last Price > 0")
            
            # Calculate theoretical premium based on last price and open interest
            combined_df['theoretical_premium'] = combined_df['openInterest'] * combined_df['lastPrice'] * 100
            
            # Apply position-based filters with POSITION ANALYSIS thresholds
            oi_filter = combined_df['openInterest'] >= POSITION_ANALYSIS_MIN_OI
            theoretical_premium_filter = combined_df['theoretical_premium'] >= POSITION_ANALYSIS_MIN_PREMIUM
            price_filter = combined_df['lastPrice'] > 0
            
            logger.info(f"  - OI filter: {oi_filter.sum()} contracts")
            logger.info(f"  - Theoretical premium filter: {theoretical_premium_filter.sum()} contracts")
            logger.info(f"  - Price filter: {price_filter.sum()} contracts")
            
            unusual_options = combined_df[oi_filter & theoretical_premium_filter & price_filter].copy()
            
            # Sort by open interest (highest positions first)
            unusual_options = unusual_options.sort_values('openInterest', ascending=False)
            logger.info(f"✅ Found {len(unusual_options)} significant positions (open interest-based)")
        
        # Sort and limit results
        if has_volume:
            unusual_options = unusual_options.sort_values('volumeToOiRatio', ascending=False)
        else:
            # Already sorted by open interest in pre-market mode
            pass
        unusual_options = unusual_options.head(MAX_RESULTS)
        
        # SIMPLIFIED ANALYSIS - DEBUGGING VERSION  
        logger.info("📊 Creating contracts with basic analysis...")
        
        # Convert to response format (simplified for debugging)
        unusual_contracts = []
        for _, row in unusual_options.iterrows():
            try:
                # BASIC CONTRACT CREATION (no expert analysis for now)
                # Calculate premium based on mode
                if has_volume:
                    premium = float(row['premiumSpent'])
                    ratio = float(row['volumeToOiRatio'])
                else:
                    premium = float(row['theoretical_premium'])
                    ratio = 0.0  # No volume ratio in pre-market
                
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
                    # SIMPLIFIED EXPERT FIELDS
                    moneyness="OTM",  # Fixed for debugging
                    distanceFromStrike=0.0,  # Fixed for debugging
                    unusualityLevel="UNUSUAL",  # Fixed for debugging
                    daysToExpiration=int(row['dte']),
                    timeDecayRisk="MEDIUM",  # Fixed for debugging
                    strategicSignal="OPTIONS FLOW"  # Fixed for debugging
                )
                unusual_contracts.append(contract)
            except Exception as e:
                logger.error(f"Error creating contract: {e}")
                continue
        
        # SIMPLIFIED MARKET SENTIMENT
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
        
        # ENHANCED INSIGHTS with data source information
        market_mode = "LIVE TRADING" if has_volume else "POSITION ANALYSIS"
        analysis_type = "Volume-based" if has_volume else "Open Interest-based"
        mode_icon = "🔴" if has_volume else "🔵"
        
        logger.info(f"🎯 FINAL MODE DECISION: {market_mode} (has_volume={has_volume})")
        logger.info(f"🎯 ANALYSIS TYPE: {analysis_type}")
        
        top_signals = [
            f"{mode_icon} {market_mode} MODE - {analysis_type} analysis",
            f"Found {len(unusual_contracts)} {'unusual contracts' if has_volume else 'significant positions'}",
            f"Data source: {data_source.value.upper()}",
            f"Data quality: {'Excellent' if data_source == DataSource.IBKR else 'Good'}"
        ]
        
        if has_volume:
            top_signals.append(f"Filters: Vol/OI≥{MIN_VOL_OI_RATIO}, Vol≥{LIVE_TRADING_MIN_VOLUME}, Premium≥${LIVE_TRADING_MIN_PREMIUM:,.0f}")
        else:
            top_signals.append(f"Filters: OI≥{POSITION_ANALYSIS_MIN_OI}, Premium≥${POSITION_ANALYSIS_MIN_PREMIUM:,.0f}")
        
        if quality_info.get("fallback_used"):
            top_signals.append("⚠️ Using fallback data source")
        
        risk_warnings = []
        if quality_info.get("errors"):
            risk_warnings.extend([f"Data warning: {error}" for error in quality_info["errors"]])
        
        # Create comprehensive data quality info
        data_quality_score = 95 if data_source == DataSource.IBKR else 75
        
        # IBKR specific metrics
        ibkr_metrics = None
        if data_source == DataSource.IBKR and ibkr_connection_status.connected:
            ibkr_metrics = IBKRDataMetrics(
                real_time_data=True,
                market_data_type=1,  # Live data
                last_trade_time=datetime.now().isoformat()
            )
        
        data_quality = DataQualityInfo(
            data_source=data_source,
            last_updated=datetime.now().isoformat(),
            data_quality_score=data_quality_score,
            warnings=quality_info.get("errors", []),
            ibkr_metrics=ibkr_metrics,
            ibkr_connection=ibkr_connection_status if data_source == DataSource.IBKR else None
        )
        
        logger.info(f"✅ Enhanced analysis complete for {ticker_symbol}: {len(unusual_contracts)} contracts from {data_source.value}, {market_sentiment.netSentiment} sentiment")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing {ticker_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error analyzing ticker '{ticker_symbol}'")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Unusual Options Activity API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze/{ticker}",
            "docs": "/docs"
        }
    }

@app.get("/api/analyze/{ticker}", response_model=UOAResponse, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_ticker(
    ticker: str = Path(..., description="Stock ticker symbol (e.g., TSLA, AAPL)"),
    mode: str = "auto"  # "live", "position", or "auto"
):
    """
    Analyze unusual options activity for a given ticker.
    
    - **ticker**: Stock ticker symbol (case insensitive)
    - **mode**: Analysis mode - "live" (volume-based), "position" (open interest-based), or "auto" (automatic detection)
    
    Returns a list of unusual option contracts based on volume/OI ratio and other filters.
    """
    logger.info(f"Analyzing unusual options activity for ticker: {ticker} in mode: {mode}")
    
    try:
        result = analyze_options_data(ticker, mode)
        logger.info(f"Analysis complete for {ticker}. Found {len(result.unusualContracts)} unusual contracts.")
        return result
        
    except HTTPException as e:
        logger.error(f"HTTP error for ticker {ticker}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error for ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error analyzing ticker '{ticker.upper()}'")

@app.get("/api/ibkr/status")
async def get_ibkr_status():
    """
    Get IBKR connection status and configuration
    """
    global ibkr_client, ibkr_connection_status
    
    return {
        "ibkr_enabled": ENABLE_IBKR,
        "use_ibkr_primary": USE_IBKR_PRIMARY,
        "fallback_to_yfinance": FALLBACK_TO_YFINANCE,
        "connection_status": ibkr_connection_status.dict(),
        "client_initialized": ibkr_client is not None,
        "configuration": {
            "host": config.get('IBKR_CONNECTION', 'host', fallback='127.0.0.1'),
            "port": int(config.get('IBKR_CONNECTION', 'port', fallback=7497)),
            "client_id": int(config.get('IBKR_CONNECTION', 'client_id', fallback=0)),
            "connection_timeout": int(config.get('IBKR_CONNECTION', 'connection_timeout', fallback=10))
        }
    }

@app.post("/api/ibkr/connect")
async def connect_ibkr():
    """
    Manually trigger IBKR connection
    """
    global ibkr_client, ibkr_connection_status
    
    if not ENABLE_IBKR:
        raise HTTPException(status_code=400, detail="IBKR is disabled in configuration")
    
    try:
        if ibkr_client is None:
            ibkr_client = IBKRClient('config.ini')
        
        if ibkr_connection_status.connected:
            return {
                "message": "IBKR already connected",
                "status": ibkr_connection_status.dict()
            }
        
        logger.info("Manual IBKR connection requested")
        ibkr_connection_status = ibkr_client.connect_to_ibkr()
        
        if ibkr_connection_status.connected:
            return {
                "message": "Successfully connected to IBKR",
                "status": ibkr_connection_status.dict()
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to connect to IBKR: {ibkr_connection_status.error_message}"
            )
            
    except Exception as e:
        logger.error(f"Manual IBKR connection failed: {e}")
        raise HTTPException(status_code=500, detail=f"IBKR connection error: {str(e)}")

@app.post("/api/ibkr/disconnect")
async def disconnect_ibkr():
    """
    Disconnect from IBKR
    """
    global ibkr_client, ibkr_connection_status
    
    if ibkr_client and ibkr_connection_status.connected:
        try:
            ibkr_client.disconnect_from_ibkr()
            ibkr_connection_status = IBKRConnectionStatus(connected=False)
            return {"message": "Successfully disconnected from IBKR"}
        except Exception as e:
            logger.error(f"IBKR disconnection error: {e}")
            raise HTTPException(status_code=500, detail=f"Disconnection error: {str(e)}")
    else:
        return {"message": "IBKR was not connected"}

@app.get("/api/ibkr/test/{ticker}")
async def test_ibkr_data(ticker: str = Path(..., description="Stock ticker for IBKR data test")):
    """
    Test IBKR data retrieval for a specific ticker
    """
    global ibkr_client, ibkr_connection_status
    
    if not ENABLE_IBKR:
        raise HTTPException(status_code=400, detail="IBKR is disabled in configuration")
    
    if not ibkr_client or not ibkr_connection_status.connected:
        raise HTTPException(status_code=503, detail="IBKR not connected. Use /api/ibkr/connect first")
    
    try:
        ticker_symbol = ticker.upper()
        logger.info(f"Testing IBKR data retrieval for {ticker_symbol}")
        
        # Test data retrieval
        start_time = time.time()
        options_df = get_options_data_ibkr(ticker_symbol)
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        
        # Analyze the data
        test_results = {
            "ticker": ticker_symbol,
            "test_timestamp": datetime.now().isoformat(),
            "connection_status": "Connected",
            "data_retrieval": {
                "success": True,
                "contracts_found": len(options_df),
                "retrieval_time_seconds": round(retrieval_time, 2),
                "columns_available": list(options_df.columns) if not options_df.empty else [],
                "sample_data": options_df.head(3).to_dict('records') if not options_df.empty else []
            },
            "data_quality": {
                "has_bid_ask": 'bid' in options_df.columns and 'ask' in options_df.columns,
                "has_greeks": any(col in options_df.columns for col in ['delta', 'gamma', 'theta', 'vega']),
                "has_volume_oi": 'volume' in options_df.columns and 'open_interest' in options_df.columns,
                "real_time_data": True,
                "data_freshness": "Live"
            },
            "performance": {
                "fast_retrieval": retrieval_time < 5.0,
                "adequate_coverage": len(options_df) > 10,
                "quality_score": 95
            }
        }
        
        logger.info(f"✅ IBKR test successful: {len(options_df)} contracts in {retrieval_time:.2f}s")
        return test_results
        
    except Exception as e:
        logger.error(f"IBKR test failed for {ticker_symbol}: {e}")
        
        error_results = {
            "ticker": ticker_symbol,
            "test_timestamp": datetime.now().isoformat(),
            "connection_status": "Connected" if ibkr_connection_status.connected else "Disconnected",
            "data_retrieval": {
                "success": False,
                "error": str(e),
                "contracts_found": 0,
                "retrieval_time_seconds": 0
            },
            "recommendations": [
                "Check if TWS/Gateway is running",
                "Verify ticker symbol is valid",
                "Ensure market is open for real-time data",
                "Check IBKR account permissions"
            ]
        }
        
        return error_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
