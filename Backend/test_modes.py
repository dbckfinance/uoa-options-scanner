#!/usr/bin/env python3
"""
Test script to compare Live Trading vs Position Analysis modes
"""
import requests
import json
import time

def test_mode(ticker, mode):
    """Test a specific mode and return results"""
    url = f"http://localhost:8000/api/analyze/{ticker}?mode={mode}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                'mode': mode,
                'ticker': data['ticker'],
                'total_contracts': data['totalContracts'],
                'unusual_contracts': len(data['unusualContracts']),
                'top_signals': data['topSignals'][:3],  # First 3 signals
                'underlying_price': data['underlyingPrice']
            }
        else:
            return {'mode': mode, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'mode': mode, 'error': str(e)}

def main():
    print("🧪 Testing Live Trading vs Position Analysis modes")
    print("=" * 60)
    
    ticker = "AAPL"
    
    # Test Live Trading mode
    print(f"\n🔴 Testing LIVE TRADING mode for {ticker}...")
    live_result = test_mode(ticker, "live")
    
    time.sleep(1)  # Small delay between requests
    
    # Test Position Analysis mode
    print(f"\n🔵 Testing POSITION ANALYSIS mode for {ticker}...")
    position_result = test_mode(ticker, "position")
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 COMPARISON RESULTS")
    print("=" * 60)
    
    for result in [live_result, position_result]:
        if 'error' in result:
            print(f"\n❌ {result['mode'].upper()}: {result['error']}")
        else:
            print(f"\n✅ {result['mode'].upper()}:")
            print(f"   Ticker: {result['ticker']}")
            print(f"   Total Contracts: {result['total_contracts']}")
            print(f"   Unusual Contracts: {result['unusual_contracts']}")
            print(f"   Underlying Price: ${result['underlying_price']:.2f}")
            print(f"   Top Signals:")
            for signal in result['top_signals']:
                print(f"     - {signal}")
    
    # Compare results
    if 'error' not in live_result and 'error' not in position_result:
        print(f"\n🔍 DIFFERENCES:")
        print(f"   Unusual contracts difference: {abs(live_result['unusual_contracts'] - position_result['unusual_contracts'])}")
        print(f"   Live Trading: {live_result['unusual_contracts']} contracts")
        print(f"   Position Analysis: {position_result['unusual_contracts']} contracts")
        
        if live_result['unusual_contracts'] == position_result['unusual_contracts']:
            print("   ⚠️  WARNING: Both modes return the same number of contracts!")
        else:
            print("   ✅ SUCCESS: Modes return different results as expected!")

if __name__ == "__main__":
    main()
