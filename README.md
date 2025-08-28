# Unusual Options Activity (UOA) Web Application

A full-stack web application for on-demand analysis of unusual options activity for US stock tickers. Built with a Python FastAPI backend and React TypeScript frontend.

## 🚀 Features

### Backend (Python/FastAPI)
- **Real-time Data**: Fetches live options data using yfinance
- **Smart Filtering**: Configurable parameters for identifying unusual activity
- **RESTful API**: Clean, documented API with automatic OpenAPI documentation
- **Error Handling**: Comprehensive error handling with detailed responses
- **Performance**: Async FastAPI for high performance
- **CORS Ready**: Configured for cross-origin requests

### Frontend (React/TypeScript)
- **Modern UI**: Professional, responsive design with Material-UI
- **Real-time Analysis**: Enter any US ticker for instant analysis
- **Advanced Data Grid**: Sortable, filterable table with professional styling
- **Visual Indicators**: Color-coded importance levels and type indicators
- **Error Management**: Graceful error handling with user-friendly messages
- **Loading States**: Professional loading indicators and skeleton screens

## 🏗️ Architecture

```
Option screener/
├── Backend/                 # Python FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── models.py           # Pydantic data models
│   ├── config.ini          # Configuration parameters
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
│
├── Frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API communication
│   │   ├── types/          # TypeScript definitions
│   │   └── App.tsx         # Main application
│   ├── package.json        # Node.js dependencies
│   └── README.md           # Frontend documentation
│
└── README.md               # This file
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the Backend directory:
```bash
cd Backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 How It Works

1. **User Input**: Enter a US stock ticker (e.g., TSLA, AAPL) in the frontend
2. **Data Fetching**: Backend fetches real-time options data from Yahoo Finance
3. **Analysis**: Applies configurable filters to identify unusual activity:
   - Volume to Open Interest ratio ≥ 1.0
   - Minimum volume threshold (50 contracts)
   - Minimum open interest (10 contracts)
   - Premium spent threshold ($1,000+)
   - Days to expiration filter (1-45 days)
4. **Display**: Results shown in a professional data grid with visual indicators

## 🎯 Unusual Activity Criteria

The application identifies unusual options activity based on:

- **Volume/OI Ratio**: High volume relative to open interest
- **Volume Threshold**: Minimum trading volume requirements
- **Premium Flow**: Significant dollar amounts being traded
- **Time Decay**: Focus on near-term expiration dates
- **Open Interest**: Sufficient existing positions

All parameters are configurable in `Backend/config.ini`.

## 🔧 Configuration

### Backend Configuration (`Backend/config.ini`)

```ini
[FILTERING]
min_volume_oi_ratio = 1.0      # Minimum Vol/OI ratio
min_volume = 50                # Minimum volume
min_open_interest = 10         # Minimum open interest
max_dte = 45                   # Maximum days to expiration
min_dte = 1                    # Minimum days to expiration
min_premium_spent = 1000.0     # Minimum premium in USD
max_results = 100              # Maximum results returned
```

## 📱 User Interface

The frontend provides a modern, professional interface with:

- **Clean Input**: Prominent ticker input with validation
- **Visual Feedback**: Loading states, error messages, and success indicators
- **Data Visualization**: Professional data grid with sorting and filtering
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Accessibility**: Follows WCAG guidelines for accessibility

## 🔍 API Documentation

Once the backend is running, visit:
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

### Main Endpoint

**GET** `/api/analyze/{ticker}`

Returns unusual options activity analysis for the specified ticker.

## 🚨 Error Handling

The application provides comprehensive error handling for:
- Invalid ticker symbols
- Network connectivity issues
- API timeouts
- Data unavailability
- Server errors

All errors include user-friendly messages and appropriate HTTP status codes.

## 🔮 Future Enhancements

Potential improvements could include:
- Historical analysis and trends
- Real-time streaming updates
- Options strategy suggestions
- Portfolio tracking
- Alert notifications
- Mobile app version

## 📄 License

This project is for educational and personal use. Options data is provided by Yahoo Finance and subject to their terms of service.

## ⚠️ Disclaimer

This tool is for educational purposes only. Options trading involves significant risk. Past performance does not guarantee future results. Always consult with a financial advisor before making investment decisions.

