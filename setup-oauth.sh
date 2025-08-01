#!/bin/bash

# 🔐 Script de configuration OAuth pour KanterMator
# Exécutez ce script après avoir téléchargé le fichier credentials depuis Google Cloud Console

echo "🔐 Configuration OAuth KanterMator"
echo ""

# Création du dossier credentials
mkdir -p credentials

echo "📂 Dossier credentials créé"
echo ""

echo "📋 INSTRUCTIONS :"
echo ""
echo "1. Dans Google Cloud Console > APIs & Services > Credentials"
echo "2. Cliquez sur votre OAuth Client ID créé"
echo "3. Cliquez 'DOWNLOAD JSON' en haut à droite"
echo "4. Renommez le fichier téléchargé en 'google-credentials.json'"
echo "5. Placez-le dans le dossier credentials/ de ce projet"
echo ""

echo "🔧 Structure attendue :"
echo "mega-flemme/"
echo "├── credentials/"
echo "│   ├── google-credentials.json  ← Fichier OAuth téléchargé"
echo "│   └── token.json              ← Sera créé automatiquement"
echo "└── ..."
echo ""

echo "⚠️  SÉCURITÉ :"
echo "- Ne commitez JAMAIS ces fichiers dans Git"
echo "- Le .gitignore les exclut déjà"
echo "- Gardez ces credentials privés"
echo ""

echo "🚀 Après avoir placé le fichier, testez avec :"
echo "docker-compose up"
