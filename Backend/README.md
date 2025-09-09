# Unusual Options Activity Backend

A FastAPI backend service for analyzing unusual options activity using yfinance data.

## Features

- RESTful API with FastAPI
- Real-time options data from Yahoo Finance
- Configurable filtering parameters
- Comprehensive error handling
- Interactive API documentation
- CORS enabled for frontend integration

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.ini` to adjust filtering parameters:

- `min_volume_oi_ratio`: Minimum Volume/OI ratio (default: 1.0)
- `min_volume`: Minimum volume threshold (default: 50)
- `min_open_interest`: Minimum open interest (default: 10)
- `max_dte`: Maximum days to expiration (default: 45)
- `min_dte`: Minimum days to expiration (default: 1)
- `min_premium_spent`: Minimum premium spent in USD (default: 1000.0)
- `max_results`: Maximum results to return (default: 100)

## Running the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Interactive docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## API Endpoints

### GET /api/analyze/{ticker}

Analyze unusual options activity for a given ticker.

**Parameters:**
- `ticker` (path): Stock ticker symbol (e.g., TSLA, AAPL)

**Response:**
```json
{
  "ticker": "TSLA",
  "analysisDate": "2024-01-01T12:00:00",
  "underlyingPrice": 250.00,
  "totalContracts": 1500,
  "unusualContracts": [
    {
      "contractSymbol": "TSLA240119C00300000",
      "strike": 300.0,
      "type": "call",
      "expirationDate": "2024-01-19",
      "lastPrice": 5.50,
      "volume": 1000,
      "openInterest": 500,
      "volumeToOiRatio": 2.0,
      "premiumSpent": 550000.0,
      "underlyingPrice": 250.00
    }
  ]
}
```

## 🚀 IBKR Integration (Premium Data)

This API now supports **Interactive Brokers (IBKR)** for professional-grade options data:

### Quick Setup
1. **Install IBKR dependencies:**
   ```bash
   pip install ibapi==10.19.2
   ```

2. **Configure IBKR in `config.ini`:**
   ```ini
   [IBKR_CONNECTION]
   enable_ibkr = true
   use_ibkr_primary = true
   fallback_to_yfinance = true
   ```

3. **Start TWS/Gateway** (port 7497 for Paper Trading)

4. **Test connection:**
   ```bash
   curl http://localhost:8000/api/ibkr/status
   ```

### IBKR Endpoints

#### Check IBKR Status
```
GET /api/ibkr/status
```

#### Connect to IBKR
```
POST /api/ibkr/connect
```

#### Test IBKR Data
```
GET /api/ibkr/test/{ticker}
```

### Data Quality Comparison

| Feature | yfinance | IBKR |
|---------|----------|------|
| **Real-time data** | ❌ 15-20 min delay | ✅ Live |
| **Bid/Ask spreads** | ❌ | ✅ |
| **Greeks** | ❌ | ✅ |
| **Data quality** | 75/100 | 95/100 |
| **Cost** | Free | $1.50/month OPRA |

### Enhanced Response with IBKR

```json
{
  "ticker": "TSLA",
  "dataQuality": {
    "data_source": "ibkr",
    "data_quality_score": 95,
    "ibkr_metrics": {
      "real_time_data": true,
      "market_data_type": 1
    }
  },
  "unusualContracts": [
    {
      "strike": 300.0,
      "lastPrice": 5.50,
      "bid": 5.40,
      "ask": 5.60,
      "impliedVolatility": 0.45,
      "delta": 0.65,
      "dataSource": "ibkr"
    }
  ]
}
```

📖 **Full IBKR documentation:** [IBKR_INTEGRATION.md](IBKR_INTEGRATION.md)

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `404`: Ticker not found or no data available
- `500`: Internal server error
- `503`: IBKR service unavailable

Error responses include detailed messages:
```json
{
  "detail": "Could not fetch data for ticker 'XYZ'",
  "data_sources_tried": ["ibkr", "yfinance"]
}
```

