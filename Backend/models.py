from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OptionContract(BaseModel):
    """Enhanced option contract model with expert trading analysis."""
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
    
    # EXPERT ANALYSIS FIELDS
    moneyness: str  # 'ITM', 'ATM', 'OTM', 'Deep-OTM'
    distanceFromStrike: float  # Percentage distance from current price
    unusualityLevel: str  # 'UNUSUAL', 'HIGH', 'EXTREME' based on ratio
    daysToExpiration: int
    timeDecayRisk: str  # 'LOW', 'MEDIUM', 'HIGH' based on DTE
    strategicSignal: str  # Trading interpretation

class MarketSentiment(BaseModel):
    """Market sentiment analysis from options flow."""
    totalCallVolume: int
    totalPutVolume: int
    callPutRatio: float
    bullishSignals: int
    bearishSignals: int
    netSentiment: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'

class UOAResponse(BaseModel):
    """Enhanced response model with expert trading insights."""
    ticker: str
    analysisDate: str
    underlyingPrice: float
    totalContracts: int
    unusualContracts: List[OptionContract]
    
    # EXPERT INSIGHTS
    marketSentiment: MarketSentiment
    topSignals: List[str]  # Key insights for traders
    riskWarnings: List[str]  # Risk management insights

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    ticker: Optional[str] = None

