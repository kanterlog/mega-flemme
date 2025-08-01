#!/bin/bash

echo "🔍 DIAGNOSTIC SYLVIE V3.0 - $(date)"
echo "=================================="

# Informations système
echo "📱 ENVIRONNEMENT SYSTÈME"
echo "OS: $(uname -s) $(uname -r)"
echo "Architecture: $(uname -m)"
echo ""

# Versions Node.js/npm
echo "🔧 VERSIONS OUTILS"
echo "Node.js: $(node --version 2>/dev/null || echo 'NON INSTALLÉ')"
echo "npm: $(npm --version 2>/dev/null || echo 'NON INSTALLÉ')"
echo "npx: $(npx --version 2>/dev/null || echo 'NON INSTALLÉ')"
echo ""

# Vérification du projet
PROJECT_DIR="/Users/kanter/Desktop/mega-flemme/sylvie-v3-clean"
echo "📁 VÉRIFICATION PROJET: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    echo "✅ Répertoire existe"
    
    # Package.json
    if [ -f "package.json" ]; then
        echo "✅ package.json présent"
        echo "Scripts disponibles:"
        cat package.json | grep -A 10 '"scripts"' | head -15
    else
        echo "❌ package.json manquant"
    fi
    
    # Node modules
    if [ -d "node_modules" ]; then
        echo "✅ node_modules présent ($(ls node_modules | wc -l) packages)"
        
        # Vérification Next.js
        if [ -f "node_modules/next/dist/bin/next" ]; then
            echo "✅ Binary Next.js trouvé"
            echo "Permissions: $(ls -la node_modules/next/dist/bin/next)"
        else
            echo "❌ Binary Next.js manquant"
        fi
    else
        echo "❌ node_modules manquant"
    fi
    
    # Test npm dans le projet
    echo ""
    echo "🧪 TEST NPM DANS LE PROJET"
    echo "Commande: npm run"
    npm run 2>&1 | head -10
    
else
    echo "❌ Répertoire projet non trouvé: $PROJECT_DIR"
fi

echo ""
echo "🔍 CACHE ET CONFIGURATION NPM"
echo "Cache npm: $(npm config get cache)"
echo "Registre npm: $(npm config get registry)"
echo "Prefix global: $(npm config get prefix)"

echo ""
echo "💾 ESPACE DISQUE"
df -h /Users/kanter/Desktop/

echo ""
echo "🔚 Diagnostic terminé - $(date)"
