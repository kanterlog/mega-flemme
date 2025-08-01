#!/bin/bash

echo "🔄 ÉTAPE 1: SAUVEGARDE DU CODE FONCTIONNEL"
echo "=========================================="

# Création du dossier de sauvegarde
BACKUP_DIR="$HOME/Desktop/sylvie-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Dossier de sauvegarde: $BACKUP_DIR"

# Sauvegarde des fichiers critiques
SOURCE_DIR="/Users/kanter/Desktop/mega-flemme/sylvie-v3-clean"

if [ -d "$SOURCE_DIR" ]; then
    echo "✅ Projet source trouvé: $SOURCE_DIR"
    
    # Sauvegarde page-fixed.tsx
    if [ -f "$SOURCE_DIR/src/app/page-fixed.tsx" ]; then
        cp "$SOURCE_DIR/src/app/page-fixed.tsx" "$BACKUP_DIR/page-fixed.tsx"
        echo "✅ page-fixed.tsx sauvegardé"
    else
        echo "⚠️  page-fixed.tsx non trouvé"
    fi
    
    # Sauvegarde page.tsx
    if [ -f "$SOURCE_DIR/src/app/page.tsx" ]; then
        cp "$SOURCE_DIR/src/app/page.tsx" "$BACKUP_DIR/page.tsx"
        echo "✅ page.tsx sauvegardé"
    else
        echo "⚠️  page.tsx non trouvé"
    fi
    
    # Sauvegarde du store Zustand
    if [ -f "$SOURCE_DIR/src/store/sylvieStore.ts" ]; then
        cp "$SOURCE_DIR/src/store/sylvieStore.ts" "$BACKUP_DIR/sylvieStore.ts"
        echo "✅ sylvieStore.ts sauvegardé"
    else
        echo "⚠️  sylvieStore.ts non trouvé"
    fi
    
    # Sauvegarde des configurations
    if [ -f "$SOURCE_DIR/package.json" ]; then
        cp "$SOURCE_DIR/package.json" "$BACKUP_DIR/package.json"
        echo "✅ package.json sauvegardé"
    fi
    
    if [ -f "$SOURCE_DIR/tsconfig.json" ]; then
        cp "$SOURCE_DIR/tsconfig.json" "$BACKUP_DIR/tsconfig.json"
        echo "✅ tsconfig.json sauvegardé"
    fi
    
    if [ -f "$SOURCE_DIR/tailwind.config.ts" ]; then
        cp "$SOURCE_DIR/tailwind.config.ts" "$BACKUP_DIR/tailwind.config.ts"
        echo "✅ tailwind.config.ts sauvegardé"
    fi
    
    if [ -f "$SOURCE_DIR/next.config.js" ]; then
        cp "$SOURCE_DIR/next.config.js" "$BACKUP_DIR/next.config.js"
        echo "✅ next.config.js sauvegardé"
    fi
    
    echo ""
    echo "📋 RÉSUMÉ SAUVEGARDE:"
    ls -la "$BACKUP_DIR"
    
    echo ""
    echo "✅ ÉTAPE 1 TERMINÉE - Tous les fichiers sont sauvegardés dans:"
    echo "   $BACKUP_DIR"
    
else
    echo "❌ Projet source non trouvé: $SOURCE_DIR"
    exit 1
fi

echo ""
echo "🚀 PRÊT POUR ÉTAPE 2: Création du nouveau projet"
echo "   Commande à exécuter ensuite:"
echo "   cd /Users/kanter/Desktop/"
echo "   npx create-next-app@14 sylvie-v3-recovery --typescript --tailwind --eslint --app --src-dir"
