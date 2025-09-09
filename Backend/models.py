from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum

class DataSource(str, Enum):
    """Enumeration of data sources"""
    YFINANCE = "yfinance"
    IBKR = "ibkr"
    HYBRID = "hybrid"

class IBKRConnectionStatus(BaseModel):
    """IBKR connection status information"""
    connected: bool
    connection_time: Optional[str] = None
    tws_version: Optional[str] = None
    account_id: Optional[str] = None
    server_version: Optional[int] = None
    error_message: Optional[str] = None

class IBKRDataMetrics(BaseModel):
    """IBKR specific data quality metrics"""
    bid_ask_spread: Optional[float] = None
    market_data_type: Optional[int] = None  # 1=Live, 2=Frozen, 3=Delayed, 4=Delayed-Frozen
    last_trade_time: Optional[str] = None
    volume_today: Optional[int] = None
    real_time_data: bool = False

class DataQualityInfo(BaseModel):
    """Information about data quality and reliability."""
    data_source: DataSource
    last_updated: str
    exchange: Optional[str] = None
    market_cap: Optional[int] = None
    volume_24h: Optional[int] = None
    data_quality_score: int  # 0-100 score
    warnings: List[str] = []  # Data quality warnings
    
    # IBKR specific metrics
    ibkr_metrics: Optional[IBKRDataMetrics] = None
    ibkr_connection: Optional[IBKRConnectionStatus] = None

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
    
    # IBKR ENHANCED FIELDS (optional, only when using IBKR)
    bid: Optional[float] = None
    ask: Optional[float] = None
    bidSize: Optional[int] = None
    askSize: Optional[int] = None
    impliedVolatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    
    # Data source information
    dataSource: DataSource = DataSource.YFINANCE
    dataQuality: Optional[int] = None  # 0-100 score for this specific contract

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
    
    # DATA QUALITY INFORMATION
    dataQuality: DataQualityInfo

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    ticker: Optional[str] = None

