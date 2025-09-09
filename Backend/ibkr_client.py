"""
IBKR Client Module for Option Screener
Handles connection, data retrieval, and error management for Interactive Brokers
"""

import time
import threading
import logging
import configparser
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
import pandas as pd

# IBKR imports
try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.common import TickerId, TickAttrib
    from ibapi.ticktype import TickType
    IBKR_AVAILABLE = True
except ImportError:
    IBKR_AVAILABLE = False
    print("⚠️ IBKR (ibapi) not available. Install with: pip install ibapi")
    
    # Create dummy base classes when IBKR is not available
    class EWrapper:
        pass
    
    class EClient:
        def __init__(self, wrapper):
            pass

from models import IBKRConnectionStatus, IBKRDataMetrics, DataSource

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class OptionsContract:
    """Internal representation of an options contract"""
    contract_id: int
    symbol: str
    strike: float
    expiration: str
    right: str  # 'C' or 'P'
    exchange: str
    currency: str
    
    # Market data
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    last_size: Optional[int] = None
    volume: Optional[int] = None
    open_interest: Optional[int] = None
    
    # Greeks and metrics
    implied_vol: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    
    # Data quality
    market_data_type: Optional[int] = None
    last_trade_time: Optional[str] = None
    data_ready: bool = False

class IBKRClient(EWrapper, EClient):
    """
    Enhanced IBKR client for options data retrieval with robust error handling
    """
    
    def __init__(self, config_file: str = "config.ini"):
        if not IBKR_AVAILABLE:
            raise ImportError("IBKR API not available. Install ibapi package.")
        
        EClient.__init__(self, self)
        
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Connection settings
        self.host = self.config.get('IBKR_CONNECTION', 'host', fallback='127.0.0.1')
        self.port = int(self.config.get('IBKR_CONNECTION', 'port', fallback=7497))
        self.client_id = int(self.config.get('IBKR_CONNECTION', 'client_id', fallback=0))
        self.connection_timeout = int(self.config.get('IBKR_CONNECTION', 'connection_timeout', fallback=10))
        self.max_retries = int(self.config.get('IBKR_CONNECTION', 'max_retry_attempts', fallback=3))
        self.retry_delay = int(self.config.get('IBKR_CONNECTION', 'retry_delay', fallback=5))
        
        # State management
        self.connected = False
        self.connection_time = None
        self.next_req_id = 1
        self.pending_requests = {}
        self.options_data = {}
        self.account_info = {}
        
        # Connection status
        self.connection_status = IBKRConnectionStatus(connected=False)
        
        # Threading
        self.api_thread = None
        self.running = False
        
        logger.info("IBKRClient initialized")
    
    def connect_to_ibkr(self) -> IBKRConnectionStatus:
        """
        Connect to IBKR TWS/Gateway with retry logic
        """
        logger.info(f"Attempting to connect to IBKR at {self.host}:{self.port}")
        
        for attempt in range(self.max_retries):
            try:
                # Attempt connection
                self.connect(self.host, self.port, self.client_id)
                
                # Start API thread
                self.api_thread = threading.Thread(target=self.run, daemon=True)
                self.api_thread.start()
                
                # Wait for connection confirmation
                start_time = time.time()
                while time.time() - start_time < self.connection_timeout:
                    if self.connected:
                        self.connection_time = datetime.now().isoformat()
                        logger.info(f"✅ Successfully connected to IBKR on attempt {attempt + 1}")
                        
                        self.connection_status = IBKRConnectionStatus(
                            connected=True,
                            connection_time=self.connection_time,
                            server_version=self.serverVersion() if hasattr(self, 'serverVersion') else None
                        )
                        
                        return self.connection_status
                    time.sleep(0.1)
                
                # Connection timeout
                logger.warning(f"Connection attempt {attempt + 1} timed out")
                self.disconnect()
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            
            if attempt < self.max_retries - 1:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        # All attempts failed
        error_msg = f"Failed to connect to IBKR after {self.max_retries} attempts"
        logger.error(error_msg)
        
        self.connection_status = IBKRConnectionStatus(
            connected=False,
            error_message=error_msg
        )
        
        return self.connection_status
    
    def disconnect_from_ibkr(self):
        """Safely disconnect from IBKR"""
        logger.info("Disconnecting from IBKR...")
        self.running = False
        self.connected = False
        self.disconnect()
        
        if self.api_thread and self.api_thread.is_alive():
            self.api_thread.join(timeout=2)
        
        self.connection_status.connected = False
        logger.info("Disconnected from IBKR")
    
    # EWrapper callback methods
    def connectAck(self):
        """Called when connection is acknowledged"""
        logger.info("IBKR connection acknowledged")
    
    def nextValidId(self, orderId: int):
        """Called when connection is fully established"""
        logger.info(f"IBKR connection established. Next valid ID: {orderId}")
        self.next_req_id = orderId
        self.connected = True
        self.running = True
    
    def connectionClosed(self):
        """Called when connection is closed"""
        logger.info("IBKR connection closed")
        self.connected = False
        self.running = False
    
    def error(self, reqId: TickerId, errorCode: int, errorString: str, advancedOrderRejectJson=""):
        """Handle errors from IBKR"""
        if errorCode in [2104, 2106, 2107, 2108]:  # Market data warnings (non-critical)
            logger.debug(f"IBKR Market data info (ID: {reqId}): {errorCode} - {errorString}")
        elif errorCode in [502, 503, 504]:  # Connection errors
            logger.error(f"IBKR Connection error: {errorCode} - {errorString}")
            self.connected = False
        elif errorCode == 200:  # No security definition found
            logger.warning(f"IBKR Security not found (ID: {reqId}): {errorString}")
            if reqId in self.pending_requests:
                del self.pending_requests[reqId]
        else:
            logger.error(f"IBKR Error (ID: {reqId}): {errorCode} - {errorString}")
    
    def get_next_req_id(self) -> int:
        """Get next request ID thread-safely"""
        req_id = self.next_req_id
        self.next_req_id += 1
        return req_id
    
    def create_options_contract(self, symbol: str, expiration: str, strike: float, right: str) -> Contract:
        """Create IBKR options contract"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.lastTradingDay = expiration
        contract.strike = strike
        contract.right = right  # 'C' for call, 'P' for put
        contract.multiplier = "100"
        return contract
    
    def request_options_data(self, symbol: str, expiration: str, strikes: List[float], 
                           option_types: List[str]) -> Dict[int, OptionsContract]:
        """
        Request options data for multiple strikes and types
        """
        if not self.connected:
            raise Exception("Not connected to IBKR")
        
        requested_contracts = {}
        
        for strike in strikes:
            for option_type in option_types:
                right = 'C' if option_type.upper() == 'CALL' else 'P'
                
                # Create contract
                contract = self.create_options_contract(symbol, expiration, strike, right)
                
                # Get request ID
                req_id = self.get_next_req_id()
                
                # Create internal contract representation
                options_contract = OptionsContract(
                    contract_id=req_id,
                    symbol=symbol,
                    strike=strike,
                    expiration=expiration,
                    right=right,
                    exchange="SMART",
                    currency="USD"
                )
                
                # Store for tracking
                requested_contracts[req_id] = options_contract
                self.pending_requests[req_id] = {
                    'contract': contract,
                    'timestamp': time.time(),
                    'symbol': symbol,
                    'strike': strike,
                    'right': right
                }
                
                # Request market data
                self.reqMktData(req_id, contract, "100,101,104,105,106,107,108", False, False, [])
                
                logger.debug(f"Requested options data: {symbol} {expiration} {strike} {right} (ID: {req_id})")
        
        return requested_contracts
    
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        """Handle price ticks"""
        if reqId in self.pending_requests:
            if reqId not in self.options_data:
                self.options_data[reqId] = {}
            
            # Map tick types to fields
            if tickType == TickType.BID:
                self.options_data[reqId]['bid'] = price
            elif tickType == TickType.ASK:
                self.options_data[reqId]['ask'] = price
            elif tickType == TickType.LAST:
                self.options_data[reqId]['last'] = price
            elif tickType == TickType.HIGH:
                self.options_data[reqId]['high'] = price
            elif tickType == TickType.LOW:
                self.options_data[reqId]['low'] = price
            elif tickType == TickType.CLOSE:
                self.options_data[reqId]['close'] = price
    
    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        """Handle size ticks"""
        if reqId in self.pending_requests:
            if reqId not in self.options_data:
                self.options_data[reqId] = {}
            
            # Map tick types to fields
            if tickType == TickType.BID_SIZE:
                self.options_data[reqId]['bid_size'] = size
            elif tickType == TickType.ASK_SIZE:
                self.options_data[reqId]['ask_size'] = size
            elif tickType == TickType.LAST_SIZE:
                self.options_data[reqId]['last_size'] = size
            elif tickType == TickType.VOLUME:
                self.options_data[reqId]['volume'] = size
    
    def tickGeneric(self, reqId: TickerId, tickType: TickType, value: float):
        """Handle generic ticks"""
        if reqId in self.pending_requests:
            if reqId not in self.options_data:
                self.options_data[reqId] = {}
            
            # Map tick types to fields
            if tickType == TickType.OPTION_OPEN_INTEREST:
                self.options_data[reqId]['open_interest'] = int(value)
            elif tickType == TickType.OPTION_IMPLIED_VOL:
                self.options_data[reqId]['implied_vol'] = value
            elif tickType == TickType.OPTION_DELTA:
                self.options_data[reqId]['delta'] = value
            elif tickType == TickType.OPTION_GAMMA:
                self.options_data[reqId]['gamma'] = value
            elif tickType == TickType.OPTION_THETA:
                self.options_data[reqId]['theta'] = value
            elif tickType == TickType.OPTION_VEGA:
                self.options_data[reqId]['vega'] = value
    
    def wait_for_data(self, req_ids: List[int], timeout: int = 30) -> Dict[int, Dict]:
        """Wait for data to be received for all request IDs"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if all requests have data
            all_ready = True
            for req_id in req_ids:
                if req_id not in self.options_data or not self.options_data[req_id]:
                    all_ready = False
                    break
            
            if all_ready:
                break
            
            time.sleep(0.1)
        
        # Return collected data
        return {req_id: self.options_data.get(req_id, {}) for req_id in req_ids}
    
    def get_options_chain(self, symbol: str, max_strikes: int = 20) -> pd.DataFrame:
        """
        Get complete options chain for a symbol
        """
        if not self.connected:
            raise Exception("Not connected to IBKR")
        
        # Get stock price first to determine relevant strikes
        stock_price = self.get_stock_price(symbol)
        if not stock_price:
            raise Exception(f"Could not get stock price for {symbol}")
        
        # Get available expirations (simplified - get next few Fridays)
        expirations = self.get_next_expirations(4)  # Next 4 expirations
        
        all_options_data = []
        
        for expiration in expirations:
            # Calculate relevant strikes around current price
            strikes = self.calculate_relevant_strikes(stock_price, max_strikes)
            
            # Request data for calls and puts
            requested = self.request_options_data(
                symbol=symbol,
                expiration=expiration,
                strikes=strikes,
                option_types=['CALL', 'PUT']
            )
            
            # Wait for data
            req_ids = list(requested.keys())
            data = self.wait_for_data(req_ids, timeout=30)
            
            # Process received data
            for req_id, market_data in data.items():
                if market_data and req_id in requested:
                    contract_info = requested[req_id]
                    
                    # Combine contract info with market data
                    option_data = {
                        'contractSymbol': f"{symbol}{expiration}{contract_info.right}{int(contract_info.strike)}",
                        'symbol': symbol,
                        'strike': contract_info.strike,
                        'expiration': expiration,
                        'right': contract_info.right,
                        'type': 'call' if contract_info.right == 'C' else 'put',
                        **market_data
                    }
                    
                    all_options_data.append(option_data)
        
        return pd.DataFrame(all_options_data) if all_options_data else pd.DataFrame()
    
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        # Create stock contract
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        req_id = self.get_next_req_id()
        self.reqMktData(req_id, contract, "", False, False, [])
        
        # Wait for price data
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 second timeout
            if req_id in self.options_data and 'last' in self.options_data[req_id]:
                price = self.options_data[req_id]['last']
                self.cancelMktData(req_id)
                return price
            time.sleep(0.1)
        
        return None
    
    def calculate_relevant_strikes(self, stock_price: float, max_strikes: int) -> List[float]:
        """Calculate relevant strikes around current stock price"""
        # Round to nearest 5 or 10 depending on price level
        if stock_price < 50:
            strike_interval = 2.5
        elif stock_price < 200:
            strike_interval = 5
        else:
            strike_interval = 10
        
        strikes = []
        center_strike = round(stock_price / strike_interval) * strike_interval
        
        for i in range(-max_strikes//2, max_strikes//2 + 1):
            strike = center_strike + (i * strike_interval)
            if strike > 0:
                strikes.append(strike)
        
        return sorted(strikes)
    
    def get_next_expirations(self, count: int) -> List[str]:
        """Get next expiration dates (simplified - next Fridays)"""
        expirations = []
        current_date = datetime.now()
        
        # Find next Friday
        days_until_friday = (4 - current_date.weekday()) % 7
        if days_until_friday == 0:  # If today is Friday, get next Friday
            days_until_friday = 7
        
        next_friday = current_date + timedelta(days=days_until_friday)
        
        for i in range(count):
            exp_date = next_friday + timedelta(weeks=i)
            expirations.append(exp_date.strftime("%Y%m%d"))
        
        return expirations
    
    def get_connection_status(self) -> IBKRConnectionStatus:
        """Get current connection status"""
        return self.connection_status
    
    def cleanup(self):
        """Clean up resources"""
        if self.connected:
            self.disconnect_from_ibkr()
