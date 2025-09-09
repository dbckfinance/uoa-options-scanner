#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration IB Gateway
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ibkr_gateway():
    """Test complet de la configuration IB Gateway"""
    
    print("🚀 Test de la configuration IB Gateway")
    print("=" * 50)
    
    # 1. Test du serveur
    print("\n1. Test du serveur Option Screener...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Serveur démarré")
        else:
            print("❌ Problème serveur")
            return
    except Exception as e:
        print(f"❌ Serveur non accessible: {e}")
        return
    
    # 2. Test status IBKR
    print("\n2. Vérification du status IBKR...")
    try:
        response = requests.get(f"{BASE_URL}/api/ibkr/status")
        status = response.json()
        
        print(f"   IBKR activé: {status['ibkr_enabled']}")
        print(f"   Utilisation principale: {status['use_ibkr_primary']}")
        print(f"   Port configuré: {status['configuration']['port']}")
        print(f"   Connecté: {status['connection_status']['connected']}")
        
        if not status['connection_status']['connected']:
            print("⚠️  IBKR non connecté, tentative de connexion...")
            
            # 3. Tentative de connexion
            conn_response = requests.post(f"{BASE_URL}/api/ibkr/connect")
            if conn_response.status_code == 200:
                print("✅ Connexion IBKR réussie")
            else:
                print(f"❌ Échec connexion: {conn_response.json()}")
                return
        else:
            print("✅ IBKR déjà connecté")
            
    except Exception as e:
        print(f"❌ Erreur status IBKR: {e}")
        return
    
    # 4. Test des données
    print("\n3. Test de récupération des données...")
    test_tickers = ["AAPL", "TSLA", "MSFT"]
    
    for ticker in test_tickers:
        print(f"\n   Test {ticker}:")
        try:
            # Test IBKR direct
            response = requests.get(f"{BASE_URL}/api/ibkr/test/{ticker}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {ticker}: {result['data_retrieval']['contracts_found']} contrats en {result['data_retrieval']['retrieval_time_seconds']}s")
                
                # Test analyse complète
                analysis_response = requests.get(f"{BASE_URL}/api/analyze/{ticker}")
                if analysis_response.status_code == 200:
                    analysis = analysis_response.json()
                    data_source = analysis['dataQuality']['data_source']
                    score = analysis['dataQuality']['data_quality_score']
                    contracts = len(analysis['unusualContracts'])
                    print(f"   ✅ Analyse: {contracts} contrats inhabituels, source: {data_source}, qualité: {score}/100")
                else:
                    print(f"   ⚠️  Analyse échouée pour {ticker}")
                    
            else:
                print(f"   ❌ Test IBKR échoué pour {ticker}")
                
        except Exception as e:
            print(f"   ❌ Erreur {ticker}: {e}")
        
        time.sleep(1)  # Pause entre les tests
    
    # 5. Résumé
    print("\n" + "=" * 50)
    print("🎯 Test terminé")
    print("\nPour utiliser votre Option Screener avec IB Gateway:")
    print("1. Gardez IB Gateway ouvert et connecté")
    print("2. Utilisez: http://localhost:8000/api/analyze/TICKER")
    print("3. Vérifiez que 'data_source': 'ibkr' dans les réponses")
    print("\n📊 Votre Option Screener est prêt avec des données IBKR professionnelles!")

if __name__ == "__main__":
    test_ibkr_gateway()





