# Guide de Déploiement Vercel

## Problèmes résolus

### 1. Configuration Vercel
- ✅ Corrigé `vercel.json` pour utiliser `python3.9` au lieu de `python@3.9`
- ✅ Structure API correcte dans le dossier `api/`

### 2. API Serverless
- ✅ Ajouté `mangum` pour adapter FastAPI à Vercel
- ✅ Créé `api/requirements.txt` avec toutes les dépendances
- ✅ Créé `api/config.ini` pour la configuration

### 3. Optimisations
- ✅ Ajouté `.vercelignore` pour exclure les fichiers inutiles
- ✅ Test de configuration avec `test_vercel_setup.py`

## Structure finale

```
Option screener/
├── api/
│   ├── index.py          # Point d'entrée Vercel
│   ├── requirements.txt  # Dépendances Python
│   └── config.ini        # Configuration
├── Backend/
│   └── main.py           # Application FastAPI
├── Frontend/
│   └── dist/             # Build React (généré)
├── vercel.json           # Configuration Vercel
├── .vercelignore         # Fichiers à ignorer
└── test_vercel_setup.py  # Test de configuration
```

## Déploiement

### Méthode 1: Push Git (Recommandée)
```bash
git add .
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

### Méthode 2: Vercel CLI
```bash
vercel --prod
```

## Vérification

1. **Test local** : `python test_vercel_setup.py`
2. **URL de l'API** : `https://votre-projet.vercel.app/api/analyze/AAPL`
3. **Documentation** : `https://votre-projet.vercel.app/docs`

## Endpoints disponibles

- `GET /` - Informations API
- `GET /api/analyze/{ticker}` - Analyse des options
- `GET /api/ibkr/status` - Statut IBKR
- `GET /docs` - Documentation Swagger

## Dépannage

Si le déploiement échoue :

1. Vérifiez les logs Vercel dans le dashboard
2. Testez localement avec `python test_vercel_setup.py`
3. Vérifiez que tous les fichiers sont commités
4. Assurez-vous que le build Frontend fonctionne

## Notes importantes

- IBKR est désactivé par défaut sur Vercel (utilise yfinance)
- Les fonctions serverless ont un timeout de 10s
- Le build Frontend se fait automatiquement
- Configuration optimisée pour la production
