@echo off
echo 🚀 Démarrage automatique de l'Option Screener
echo ================================================

REM Aller dans le bon dossier
cd /d "C:\Users\chafi\Desktop\Option screener\Backend"

echo 📁 Dossier: %CD%
echo.

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo ✅ Environnement virtuel activé
echo.

REM Installer ibapi si pas déjà installé
echo 📦 Vérification d'ibapi...
python -c "import ibapi" 2>nul
if errorlevel 1 (
    echo ⚠️ ibapi non trouvé, installation en cours...
    pip install ibapi==9.81.1.post1
    echo ✅ ibapi installé
) else (
    echo ✅ ibapi déjà installé
)
echo.

REM Installer toutes les dépendances
echo 📦 Installation des dépendances...
pip install -r requirements.txt
echo ✅ Dépendances installées
echo.

REM Démarrer le serveur
echo 🚀 Démarrage de l'Option Screener...
echo.
echo 🌐 Votre Option Screener sera accessible sur: http://localhost:8000
echo 📊 Documentation API: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python main.py

pause
