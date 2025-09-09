# 🚀 Interactive Brokers (IBKR) Integration Guide

Ce guide explique comment utiliser l'intégration IBKR dans votre Option Screener pour obtenir des données d'options de qualité professionnelle en temps réel.

## ✨ **Avantages de l'intégration IBKR**

- **📊 Données en temps réel** (pas de délai de 15-20 minutes)
- **🎯 Qualité professionnelle** (même source que Bloomberg/Reuters)
- **📈 Volume et Open Interest précis**
- **🔍 Données de niveau 1 et 2** (bid/ask, tailles)
- **📊 Greeks complets** (delta, gamma, theta, vega)
- **🌐 Couverture mondiale** (US, Europe, Asie)

## 🛠️ **Configuration requise**

### 1. Compte IBKR
- ✅ Compte IBKR actif (Paper Trading ou Live)
- ✅ Accès aux données OPRA (US Options) - $1.50/mois
- ✅ TWS ou IB Gateway installé

### 2. Dépendances Python
```bash
pip install ibapi==10.19.2
```

### 3. Configuration TWS/Gateway
1. **Démarrer TWS ou IB Gateway**
2. **Configuration → API → Settings**
3. ✅ **Enable ActiveX and Socket Clients**
4. **Socket port:** 7497 (Paper) ou 7496 (Live)
5. **Trusted IPs:** 127.0.0.1

## ⚙️ **Configuration du système**

### 1. Fichier config.ini

```ini
[IBKR_CONNECTION]
# Interactive Brokers connection settings
host = 127.0.0.1
port = 7497  # 7497 = Paper Trading, 7496 = Live Trading
client_id = 0

# Connection timeout and retry settings
connection_timeout = 10  # seconds
max_retry_attempts = 3
retry_delay = 5  # seconds between retries

# Enable IBKR as primary data source
enable_ibkr = true
use_ibkr_primary = true  # Use IBKR as primary source, yfinance as fallback
fallback_to_yfinance = true
fallback_timeout = 5  # seconds before falling back

[IBKR_DATA_QUALITY]
# Data quality settings
min_bid_ask_spread_ratio = 0.5
min_volume_threshold = 1
max_stale_data_minutes = 5
validate_real_time_data = true
```

### 2. Modes de fonctionnement

**Mode 1: IBKR uniquement**
```ini
enable_ibkr = true
use_ibkr_primary = true
fallback_to_yfinance = false
```

**Mode 2: IBKR avec fallback yfinance** (Recommandé)
```ini
enable_ibkr = true
use_ibkr_primary = true
fallback_to_yfinance = true
```

**Mode 3: yfinance uniquement**
```ini
enable_ibkr = false
use_ibkr_primary = false
fallback_to_yfinance = true
```

## 🚀 **Démarrage et utilisation**

### 1. Démarrer TWS/Gateway
```bash
# Démarrer TWS ou IB Gateway depuis IBKR
# Assurer que l'API est activée (port 7497/7496)
```

### 2. Démarrer l'application
```bash
cd Backend
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 3. Vérifier la connexion IBKR
```bash
# Status IBKR
curl http://localhost:8000/api/ibkr/status

# Connexion manuelle (si nécessaire)
curl -X POST http://localhost:8000/api/ibkr/connect

# Test des données
curl http://localhost:8000/api/ibkr/test/AAPL
```

## 📡 **Nouveaux endpoints IBKR**

### 1. Status de connexion
```http
GET /api/ibkr/status
```

**Réponse:**
```json
{
  "ibkr_enabled": true,
  "use_ibkr_primary": true,
  "connection_status": {
    "connected": true,
    "connection_time": "2024-01-15T10:30:00",
    "server_version": 176
  },
  "configuration": {
    "host": "127.0.0.1",
    "port": 7497,
    "client_id": 0
  }
}
```

### 2. Connexion manuelle
```http
POST /api/ibkr/connect
```

### 3. Déconnexion
```http
POST /api/ibkr/disconnect
```

### 4. Test des données
```http
GET /api/ibkr/test/{ticker}
```

**Exemple:**
```bash
curl http://localhost:8000/api/ibkr/test/TSLA
```

**Réponse:**
```json
{
  "ticker": "TSLA",
  "test_timestamp": "2024-01-15T10:30:00",
  "connection_status": "Connected",
  "data_retrieval": {
    "success": true,
    "contracts_found": 150,
    "retrieval_time_seconds": 2.3,
    "sample_data": [...]
  },
  "data_quality": {
    "has_bid_ask": true,
    "has_greeks": true,
    "has_volume_oi": true,
    "real_time_data": true,
    "data_freshness": "Live"
  },
  "performance": {
    "fast_retrieval": true,
    "adequate_coverage": true,
    "quality_score": 95
  }
}
```

## 📊 **Données enrichies avec IBKR**

Avec IBKR, vos contrats d'options incluent maintenant :

```json
{
  "contractSymbol": "TSLA240119C00300000",
  "strike": 300.0,
  "type": "call",
  "lastPrice": 5.50,
  "volume": 1000,
  "openInterest": 500,
  
  // 🆕 IBKR Enhanced Fields
  "bid": 5.40,
  "ask": 5.60,
  "bidSize": 10,
  "askSize": 15,
  "impliedVolatility": 0.45,
  "delta": 0.65,
  "gamma": 0.03,
  "theta": -0.05,
  "vega": 0.12,
  
  // Data source info
  "dataSource": "ibkr",
  "dataQuality": 95
}
```

## 🔍 **Analyse des données**

### Endpoint principal enrichi
```http
GET /api/analyze/{ticker}
```

**Nouvelles informations dans la réponse:**
```json
{
  "ticker": "TSLA",
  "unusualContracts": [...],
  "topSignals": [
    "Found 15 unusual contracts",
    "Data source: IBKR",
    "Data quality: Excellent"
  ],
  "dataQuality": {
    "data_source": "ibkr",
    "data_quality_score": 95,
    "ibkr_metrics": {
      "real_time_data": true,
      "market_data_type": 1,
      "last_trade_time": "2024-01-15T10:30:00"
    },
    "ibkr_connection": {
      "connected": true,
      "connection_time": "2024-01-15T09:00:00"
    }
  }
}
```

## 🚨 **Résolution de problèmes**

### 1. Problèmes de connexion

**Erreur: "IBKR not connected"**
```bash
# Vérifier status
curl http://localhost:8000/api/ibkr/status

# Reconnecter
curl -X POST http://localhost:8000/api/ibkr/connect
```

**Erreur: "Connection refused"**
- ✅ TWS/Gateway est démarré
- ✅ API est activée dans TWS
- ✅ Port correct (7497/7496)
- ✅ IP autorisée (127.0.0.1)

### 2. Problèmes de données

**Erreur: "No options data"**
- ✅ Ticker valide
- ✅ Marché ouvert
- ✅ Permissions compte IBKR
- ✅ Abonnement OPRA actif

**Données incomplètes**
- ✅ Vérifier abonnements marché
- ✅ Permissions compte
- ✅ Configuration TWS

### 3. Performance

**Lenteur de récupération**
- ✅ Réduire max_strikes dans config
- ✅ Vérifier connexion réseau
- ✅ Utiliser IB Gateway (plus léger)

## ⚡ **Optimisation des performances**

### 1. Configuration recommandée
```ini
[IBKR_CONNECTION]
max_concurrent_requests = 10
request_timeout = 30

[IBKR_DATA_QUALITY]
min_volume_threshold = 5  # Filtrer le bruit
```

### 2. Utilisation efficace
- **Limitez les strikes** autour du prix actuel
- **Utilisez IB Gateway** au lieu de TWS complet
- **Filtrez par volume minimum** pour réduire le bruit

### 3. Monitoring
```bash
# Vérifier performance
curl http://localhost:8000/api/ibkr/test/AAPL

# Surveiller logs
tail -f logs/ibkr.log
```

## 🎯 **Meilleures pratiques**

### 1. Configuration de production
- ✅ **Compte Live** pour données temps réel
- ✅ **IB Gateway** pour stabilité
- ✅ **Surveillance automatique** de la connexion
- ✅ **Fallback yfinance** activé

### 2. Sécurité
- ✅ **IP restrictions** dans TWS
- ✅ **Monitoring** des connexions
- ✅ **Logs** détaillés

### 3. Fiabilité
- ✅ **Auto-reconnexion** configurée
- ✅ **Timeout** approprié
- ✅ **Gestion d'erreurs** robuste

## 🔄 **Migration depuis yfinance**

### Étape 1: Test en parallèle
```ini
# Configuration hybride
enable_ibkr = true
use_ibkr_primary = false  # Gardez yfinance principal
fallback_to_yfinance = true
```

### Étape 2: Validation
```bash
# Comparer les résultats
curl http://localhost:8000/api/analyze/AAPL
# Vérifier data_source dans la réponse
```

### Étape 3: Activation complète
```ini
# IBKR principal
use_ibkr_primary = true
```

## 📚 **Ressources supplémentaires**

- **Documentation IBKR API:** https://interactivebrokers.github.io/tws-api/
- **TWS Download:** https://www.interactivebrokers.com/en/trading/tws.php
- **OPRA Data:** https://www.interactivebrokers.com/en/trading/market-data.php

---

✅ **Votre Option Screener est maintenant équipé de données IBKR professionnelles !**

Pour toute question ou problème, vérifiez d'abord le status avec `/api/ibkr/status` et les logs du serveur.


