#!/bin/bash
# 🚀 Script de démarrage KanterMator + Sylvie
# Usage: ./start.sh [dev|prod|test]

MODE=${1:-dev}
echo "🤖 Démarrage de KanterMator en mode: $MODE"

case $MODE in
  "dev")
    echo "📝 Mode développement"
    echo "🔧 Démarrage des services avec Docker Compose..."
    docker-compose up -d postgres redis pgadmin
    echo "⏳ Attente des services (10s)..."
    sleep 10
    echo "🐍 Démarrage de l'application Python..."
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python -m app.main
    ;;
  
  "sylvie")
    echo "🤖 Mode Sylvie (avec agent IA)"
    echo "🔧 Démarrage des services avec Docker Compose..."
    docker-compose up -d postgres redis pgadmin
    echo "⏳ Attente des services (10s)..."
    sleep 10
    echo "🐍 Démarrage avec Sylvie..."
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python -m app.main_sylvie
    ;;
  
  "prod")
    echo "🚀 Mode production"
    echo "🐳 Démarrage complet avec Docker..."
    docker-compose up -d
    ;;
  
  "test")
    echo "🧪 Mode test"
    echo "🔧 Tests des composants..."
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python -c "
from app.services.google_auth import GoogleAuthService
from app.utils.database import db_manager
from app.utils.config import settings

print('✅ Test de configuration...')
print(f'Environment: {settings.ENVIRONMENT}')
print(f'Database URL: {settings.DATABASE_URL}')

print('✅ Test de base de données...')
health = db_manager.health_check()
print(f'Database Health: {health}')

print('✅ Test des services Google...')
try:
    auth = GoogleAuthService()
    # Test basique sans credentials
    print('Google Auth Service: Initialisé')
except Exception as e:
    print(f'Google Auth Error: {e}')

print('🎉 Tests terminés')
"
    ;;
  
  *)
    echo "❌ Mode non reconnu. Utilisez: dev, sylvie, prod, ou test"
    exit 1
    ;;
esac
