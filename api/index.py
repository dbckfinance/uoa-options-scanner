"""
Vercel API entry point - standalone FastAPI app for options analysis
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from enum import Enum

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

# Data models
class DataSource(str, Enum):
    YFINANCE = "yfinance"

class OptionContract(BaseModel):
    contractSymbol: str
    strike: float
    type: str  # 'call' or 'put'
    expirationDate: str
    lastPrice: float
    volume: int
    openInterest: int
    volumeToOiRatio: float
    premiumSpent: float
    underlyingPrice: float
    moneyness: str
    distanceFromStrike: float
    unusualityLevel: str
    daysToExpiration: int
    timeDecayRisk: str
    strategicSignal: str
    dataSource: DataSource = DataSource.YFINANCE

class MarketSentiment(BaseModel):
    totalCallVolume: int
    totalPutVolume: int
    callPutRatio: float
    bullishSignals: int
    bearishSignals: int
    netSentiment: str

class DataQualityInfo(BaseModel):
    data_source: DataSource
    last_updated: str
    data_quality_score: int
    warnings: List[str] = []

class UOAResponse(BaseModel):
    ticker: str
    analysisDate: str
    underlyingPrice: float
    totalContracts: int
    unusualContracts: List[OptionContract]
    marketSentiment: MarketSentiment
    topSignals: List[str]
    riskWarnings: List[str]
    dataQuality: DataQualityInfo

class ErrorResponse(BaseModel):
    detail: str
    ticker: Optional[str] = None

# Configuration
MIN_VOL_OI_RATIO = 2.5
MIN_VOLUME = 100
MIN_OPEN_INTEREST = 25
MAX_DTE = 45
MIN_DTE = 1
MIN_PREMIUM_SPENT = 25000.0
MAX_RESULTS = 50

def calculate_dte(expiration_date: str) -> int:
    """Calculate days to expiration."""
    try:
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
        today = datetime.now()
        return (exp_date - today).days
    except Exception:
        return 0

def get_options_data_yfinance(ticker_symbol: str) -> pd.DataFrame:
    """Get options data from yfinance."""
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
                all_options.append(calls)
            
            # Process puts
            if not options_chain.puts.empty:
                puts = options_chain.puts.copy()
                puts['type'] = 'put'
                puts['expirationDate'] = expiration
                puts['dte'] = dte
                puts['dataSource'] = DataSource.YFINANCE
                all_options.append(puts)
                
        except Exception as e:
            logger.warning(f"Error processing expiration {expiration}: {e}")
            continue
    
    if not all_options:
        raise Exception("No options data available from yfinance")
    
    return pd.concat(all_options, ignore_index=True)

def analyze_options_data(ticker_symbol: str, mode: str = "auto") -> UOAResponse:
    """Analyze unusual options activity for a given ticker."""
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
            suggested_tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "GOOGL"]
            suggestions = ", ".join([t for t in suggested_tickers if t != ticker_symbol][:5])
            raise HTTPException(
                status_code=404, 
                detail=f"Could not fetch stock data for ticker '{ticker_symbol}'. Try these popular tickers instead: {suggestions}"
            )
        
        # Get options data
        logger.info(f"📊 Getting options data for {ticker_symbol}...")
        try:
            combined_df = get_options_data_yfinance(ticker_symbol)
            
            if combined_df.empty:
                raise ValueError("No options data available")
            
            logger.info(f"✅ Retrieved {len(combined_df)} options contracts")
            
            # Filter by DTE
            combined_df['dte'] = combined_df['expirationDate'].apply(calculate_dte)
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
                
                data_quality = DataQualityInfo(
                    data_source=DataSource.YFINANCE,
                    last_updated=datetime.now().isoformat(),
                    data_quality_score=75,
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
                detail=f"Could not fetch options data for ticker '{ticker_symbol}'. Try these popular tickers instead: {suggestions}"
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
        
        if has_volume:
            # Volume-based filters
            volume_filter = combined_df['volumeToOiRatio'] >= MIN_VOL_OI_RATIO
            min_vol_filter = combined_df['volume'] >= MIN_VOLUME
            min_oi_filter = combined_df['openInterest'] >= MIN_OPEN_INTEREST
            premium_filter = combined_df['premiumSpent'] >= MIN_PREMIUM_SPENT
            
            unusual_options = combined_df[volume_filter & min_vol_filter & min_oi_filter & premium_filter].copy()
            unusual_options = unusual_options.sort_values('volumeToOiRatio', ascending=False)
            logger.info(f"✅ Found {len(unusual_options)} unusual contracts (volume-based)")
        else:
            # Position-based filters
            combined_df['theoretical_premium'] = combined_df['openInterest'] * combined_df['lastPrice'] * 100
            
            oi_filter = combined_df['openInterest'] >= MIN_OPEN_INTEREST
            theoretical_premium_filter = combined_df['theoretical_premium'] >= MIN_PREMIUM_SPENT
            price_filter = combined_df['lastPrice'] > 0
            
            unusual_options = combined_df[oi_filter & theoretical_premium_filter & price_filter].copy()
            unusual_options = unusual_options.sort_values('openInterest', ascending=False)
            logger.info(f"✅ Found {len(unusual_options)} significant positions (open interest-based)")
        
        # Limit results
        unusual_options = unusual_options.head(MAX_RESULTS)
        
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
                    moneyness="OTM",
                    distanceFromStrike=0.0,
                    unusualityLevel="UNUSUAL",
                    daysToExpiration=int(row['dte']),
                    timeDecayRisk="MEDIUM",
                    strategicSignal="OPTIONS FLOW"
                )
                unusual_contracts.append(contract)
            except Exception as e:
                logger.error(f"Error creating contract: {e}")
                continue
        
        # Market sentiment
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
            f"Data source: YFINANCE",
            f"Data quality: Good"
        ]
        
        if has_volume:
            top_signals.append(f"Filters: Vol/OI≥{MIN_VOL_OI_RATIO}, Vol≥{MIN_VOLUME}, Premium≥${MIN_PREMIUM_SPENT:,.0f}")
        else:
            top_signals.append(f"Filters: OI≥{MIN_OPEN_INTEREST}, Premium≥${MIN_PREMIUM_SPENT:,.0f}")
        
        data_quality = DataQualityInfo(
            data_source=DataSource.YFINANCE,
            last_updated=datetime.now().isoformat(),
            data_quality_score=75,
            warnings=[]
        )
        
        logger.info(f"✅ Analysis complete for {ticker_symbol}: {len(unusual_contracts)} contracts")
        
        return UOAResponse(
            ticker=ticker_symbol,
            analysisDate=datetime.now().isoformat(),
            underlyingPrice=current_price,
            totalContracts=len(combined_df),
            unusualContracts=unusual_contracts,
            marketSentiment=market_sentiment,
            topSignals=top_signals,
            riskWarnings=[],
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

# Create ASGI handler for Vercel
from mangum import Mangum
handler = Mangum(app)
