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

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `404`: Ticker not found or no data available
- `500`: Internal server error

Error responses include detailed messages:
```json
{
  "detail": "Could not fetch data for ticker 'XYZ'"
}
```

