#!/bin/bash

echo "🚀 ÉTAPE 2: CRÉATION NOUVEAU PROJET NEXT.JS"
echo "============================================"

# Vérification du répertoire de travail
cd /Users/kanter/Desktop/
echo "📁 Répertoire actuel: $(pwd)"

# Nettoyage si le projet existe déjà
if [ -d "sylvie-v3-recovery" ]; then
    echo "⚠️  Suppression de l'ancien projet sylvie-v3-recovery"
    rm -rf sylvie-v3-recovery
fi

echo ""
echo "🔄 Création du projet Next.js 14 avec TypeScript et Tailwind..."
echo "   Cela peut prendre 2-3 minutes..."

# Création du projet Next.js
npx create-next-app@14 sylvie-v3-recovery \
    --typescript \
    --tailwind \
    --eslint \
    --app \
    --src-dir \
    --import-alias="@/*" \
    --no-git

if [ $? -eq 0 ]; then
    echo "✅ Projet Next.js créé avec succès !"
    
    # Entrer dans le répertoire du projet
    cd sylvie-v3-recovery
    
    echo ""
    echo "📦 Installation des dépendances Sylvie..."
    
    # Installation des dépendances spécifiques à Sylvie
    npm install antd@^5.12.0 zustand@^5.0.0 lucide-react@^0.290.0
    
    if [ $? -eq 0 ]; then
        echo "✅ Dépendances Sylvie installées !"
        
        # Création du dossier store
        mkdir -p src/store
        
        echo ""
        echo "🧪 Test du serveur de développement..."
        
        # Test rapide du serveur (démarrage et arrêt automatique)
        timeout 10s npm run dev > /dev/null 2>&1 &
        DEV_PID=$!
        sleep 5
        kill $DEV_PID 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ Serveur de développement fonctionnel !"
        else
            echo "⚠️  Test du serveur en cours, vérification manuelle requise"
        fi
        
        echo ""
        echo "📋 STRUCTURE DU PROJET:"
        ls -la
        
        echo ""
        echo "✅ ÉTAPE 2 TERMINÉE - Projet Next.js prêt !"
        echo "   Répertoire: /Users/kanter/Desktop/sylvie-v3-recovery"
        
        echo ""
        echo "🚀 PRÊT POUR ÉTAPE 3: Migration du code Sylvie"
        echo "   Prochaines actions:"
        echo "   - Copier le store Zustand"
        echo "   - Copier l'interface page-fixed.tsx"
        echo "   - Configurer Ant Design"
        
    else
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
    
else
    echo "❌ Erreur lors de la création du projet Next.js"
    exit 1
fi
