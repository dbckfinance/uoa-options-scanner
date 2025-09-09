"""
Vercel API entry point - simple test function
"""
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

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

# Simple data models
class OptionContract(BaseModel):
    contractSymbol: str
    strike: float
    type: str
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

class MarketSentiment(BaseModel):
    totalCallVolume: int
    totalPutVolume: int
    callPutRatio: float
    bullishSignals: int
    bearishSignals: int
    netSentiment: str

class DataQualityInfo(BaseModel):
    data_source: str
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

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Unusual Options Activity API",
        "version": "1.0.0",
        "status": "working",
        "endpoints": {
            "analyze": "/api/analyze/{ticker}",
            "docs": "/docs"
        }
    }

@app.get("/api/analyze/{ticker}")
async def analyze_ticker(
    ticker: str = Path(..., description="Stock ticker symbol (e.g., TSLA, AAPL)"),
    mode: str = "auto"
):
    """
    Analyze unusual options activity for a given ticker.
    """
    logger.info(f"Analyzing ticker: {ticker} in mode: {mode}")
    
    try:
        # Simple test response
        test_contract = OptionContract(
            contractSymbol=f"{ticker}240115C00150000",
            strike=150.0,
            type="call",
            expirationDate="2024-01-15",
            lastPrice=5.25,
            volume=1000,
            openInterest=5000,
            volumeToOiRatio=0.2,
            premiumSpent=525000.0,
            underlyingPrice=145.50,
            moneyness="OTM",
            distanceFromStrike=3.1,
            unusualityLevel="UNUSUAL",
            daysToExpiration=30,
            timeDecayRisk="MEDIUM",
            strategicSignal="OPTIONS FLOW"
        )
        
        market_sentiment = MarketSentiment(
            totalCallVolume=1500,
            totalPutVolume=800,
            callPutRatio=1.88,
            bullishSignals=3,
            bearishSignals=1,
            netSentiment="BULLISH"
        )
        
        data_quality = DataQualityInfo(
            data_source="yfinance",
            last_updated="2024-01-01T12:00:00Z",
            data_quality_score=85,
            warnings=[]
        )
        
        response = UOAResponse(
            ticker=ticker.upper(),
            analysisDate="2024-01-01T12:00:00Z",
            underlyingPrice=145.50,
            totalContracts=100,
            unusualContracts=[test_contract],
            marketSentiment=market_sentiment,
            topSignals=[
                f"🔵 POSITION ANALYSIS MODE - Open Interest-based analysis",
                f"Found 1 significant positions",
                f"Data source: YFINANCE",
                f"Data quality: Good"
            ],
            riskWarnings=[],
            dataQuality=data_quality
        )
        
        logger.info(f"Analysis complete for {ticker}")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Create ASGI handler for Vercel
from mangum import Mangum
handler = Mangum(app)