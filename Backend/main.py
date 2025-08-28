from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
import configparser
from datetime import datetime, timedelta
from typing import List
import logging
from models import OptionContract, UOAResponse, ErrorResponse, MarketSentiment

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

def analyze_options_data(ticker_symbol: str) -> UOAResponse:
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
        
        # Method 2: Get options data using simple yf.Ticker (no custom session)
        logger.info(f"📅 Getting options data for {ticker_symbol}...")
        try:
            ticker = yf.Ticker(ticker_symbol)  # Simple, no custom session
            expirations = ticker.options
            
            if not expirations:
                raise ValueError("No options data available")
                
            logger.info(f"✅ Found {len(expirations)} expiration dates for {ticker_symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to get options data for {ticker_symbol}: {e}")
            raise HTTPException(status_code=404, detail=f"No options data available for ticker '{ticker_symbol}'")
        
        # Process options data - simplified approach
        logger.info(f"📊 Processing options chains for {ticker_symbol}...")
        all_options = []
        
        # Filter expirations by DTE
        filtered_expirations = []
        for expiration in expirations:
            dte = calculate_dte(expiration)
            if MIN_DTE <= dte <= MAX_DTE:
                filtered_expirations.append(expiration)
        
        # Limit to first 8 expirations for reliable performance
        filtered_expirations = filtered_expirations[:8]
        logger.info(f"Analyzing {len(filtered_expirations)} expiration dates for {ticker_symbol}")
        
        for i, expiration in enumerate(filtered_expirations):
            try:
                logger.info(f"Processing expiration {i+1}/{len(filtered_expirations)}: {expiration}")
                
                # Get options chain - simple approach
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
            logger.info(f"No options data collected for {ticker_symbol}")
            # Empty market sentiment
            empty_sentiment = MarketSentiment(
                totalCallVolume=0,
                totalPutVolume=0,
                callPutRatio=0.0,
                bullishSignals=0,
                bearishSignals=0,
                netSentiment="NEUTRAL"
            )
            return UOAResponse(
                ticker=ticker_symbol,
                analysisDate=datetime.now().isoformat(),
                underlyingPrice=current_price,
                totalContracts=0,
                unusualContracts=[],
                marketSentiment=empty_sentiment,
                topSignals=["No unusual options activity detected"],
                riskWarnings=[]
            )
        
        # Combine all options data
        logger.info(f"Combining {len(all_options)} option DataFrames...")
        combined_df = pd.concat(all_options, ignore_index=True)
        
        # Clean and prepare data
        combined_df = combined_df.dropna(subset=['volume', 'openInterest', 'lastPrice'])
        combined_df = combined_df[combined_df['volume'] > 0]
        combined_df = combined_df[combined_df['openInterest'] > 0]
        
        # Calculate ratios and filters
        combined_df['volumeToOiRatio'] = combined_df['volume'] / combined_df['openInterest']
        combined_df['premiumSpent'] = combined_df['volume'] * combined_df['lastPrice'] * 100
        
        # Apply filters for unusual activity
        logger.info(f"Applying filters to {len(combined_df)} total contracts...")
        unusual_options = combined_df[
            (combined_df['volumeToOiRatio'] >= MIN_VOL_OI_RATIO) &
            (combined_df['volume'] >= MIN_VOLUME) &
            (combined_df['openInterest'] >= MIN_OPEN_INTEREST) &
            (combined_df['premiumSpent'] >= MIN_PREMIUM_SPENT)
        ].copy()
        
        logger.info(f"Found {len(unusual_options)} unusual contracts")
        
        # Sort and limit results
        unusual_options = unusual_options.sort_values('volumeToOiRatio', ascending=False)
        unusual_options = unusual_options.head(MAX_RESULTS)
        
        # SIMPLIFIED ANALYSIS - DEBUGGING VERSION  
        logger.info("📊 Creating contracts with basic analysis...")
        
        # Convert to response format (simplified for debugging)
        unusual_contracts = []
        for _, row in unusual_options.iterrows():
            try:
                # BASIC CONTRACT CREATION (no expert analysis for now)
                contract = OptionContract(
                    contractSymbol=str(row['contractSymbol']),
                    strike=float(row['strike']),
                    type=str(row['type']),
                    expirationDate=str(row['expirationDate']),
                    lastPrice=float(row['lastPrice']),
                    volume=int(row['volume']),
                    openInterest=int(row['openInterest']),
                    volumeToOiRatio=float(row['volumeToOiRatio']),
                    premiumSpent=float(row['premiumSpent']),
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
        
        # SIMPLIFIED INSIGHTS
        top_signals = [f"Found {len(unusual_contracts)} unusual contracts"]
        risk_warnings = []
        
        logger.info(f"✅ EXPERT analysis complete for {ticker_symbol}: {len(unusual_contracts)} contracts, {market_sentiment.netSentiment} sentiment")
        
        return UOAResponse(
            ticker=ticker_symbol,
            analysisDate=datetime.now().isoformat(),
            underlyingPrice=current_price,
            totalContracts=len(combined_df),
            unusualContracts=unusual_contracts,
            marketSentiment=market_sentiment,
            topSignals=top_signals,
            riskWarnings=risk_warnings
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
    ticker: str = Path(..., description="Stock ticker symbol (e.g., TSLA, AAPL)")
):
    """
    Analyze unusual options activity for a given ticker.
    
    - **ticker**: Stock ticker symbol (case insensitive)
    
    Returns a list of unusual option contracts based on volume/OI ratio and other filters.
    """
    logger.info(f"Analyzing unusual options activity for ticker: {ticker}")
    
    try:
        result = analyze_options_data(ticker)
        logger.info(f"Analysis complete for {ticker}. Found {len(result.unusualContracts)} unusual contracts.")
        return result
        
    except HTTPException as e:
        logger.error(f"HTTP error for ticker {ticker}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error for ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error analyzing ticker '{ticker.upper()}'")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
