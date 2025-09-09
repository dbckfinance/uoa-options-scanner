#!/usr/bin/env python3
"""
Debug script to understand why modes return same results
"""
import requests
import json

def debug_mode(ticker, mode):
    """Debug a specific mode"""
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
                'top_signals': data['topSignals'],
                'underlying_price': data['underlyingPrice'],
                'market_sentiment': data['marketSentiment']
            }
        else:
            return {'mode': mode, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'mode': mode, 'error': str(e)}

def main():
    print("🔍 Debugging Live Trading vs Position Analysis modes")
    print("=" * 70)
    
    ticker = "TSLA"  # Use TSLA as it seems to have more data
    
    # Test Live Trading mode
    print(f"\n🔴 LIVE TRADING mode for {ticker}:")
    live_result = debug_mode(ticker, "live")
    
    if 'error' not in live_result:
        print(f"   Total Contracts: {live_result['total_contracts']}")
        print(f"   Unusual Contracts: {live_result['unusual_contracts']}")
        print(f"   Underlying Price: ${live_result['underlying_price']:.2f}")
        print(f"   Top Signals:")
        for i, signal in enumerate(live_result['top_signals'], 1):
            print(f"     {i}. {signal}")
        print(f"   Market Sentiment: {live_result['market_sentiment']['netSentiment']}")
    
    print("\n" + "-" * 70)
    
    # Test Position Analysis mode
    print(f"\n🔵 POSITION ANALYSIS mode for {ticker}:")
    position_result = debug_mode(ticker, "position")
    
    if 'error' not in position_result:
        print(f"   Total Contracts: {position_result['total_contracts']}")
        print(f"   Unusual Contracts: {position_result['unusual_contracts']}")
        print(f"   Underlying Price: ${position_result['underlying_price']:.2f}")
        print(f"   Top Signals:")
        for i, signal in enumerate(position_result['top_signals'], 1):
            print(f"     {i}. {signal}")
        print(f"   Market Sentiment: {position_result['market_sentiment']['netSentiment']}")
    
    # Compare
    if 'error' not in live_result and 'error' not in position_result:
        print(f"\n🔍 COMPARISON:")
        print(f"   Unusual contracts: Live={live_result['unusual_contracts']}, Position={position_result['unusual_contracts']}")
        print(f"   Total contracts: Live={live_result['total_contracts']}, Position={position_result['total_contracts']}")
        
        # Check if signals are different
        live_signals = live_result['top_signals']
        position_signals = position_result['top_signals']
        
        print(f"\n📊 SIGNAL COMPARISON:")
        for i, (live_sig, pos_sig) in enumerate(zip(live_signals, position_signals)):
            if live_sig == pos_sig:
                print(f"   {i+1}. SAME: {live_sig}")
            else:
                print(f"   {i+1}. DIFFERENT:")
                print(f"       Live: {live_sig}")
                print(f"       Position: {pos_sig}")

if __name__ == "__main__":
    main()
