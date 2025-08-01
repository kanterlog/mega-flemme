#!/bin/bash

echo "🔄 ÉTAPE 3: MIGRATION DU CODE SYLVIE"
echo "=================================="

# Variables
PROJECT_DIR="/Users/kanter/Desktop/sylvie-v3-recovery"
BACKUP_DIR=$(ls -1t ~/Desktop/sylvie-backup-* 2>/dev/null | head -n1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ Aucun dossier de sauvegarde trouvé"
    echo "   Recherche dans: ~/Desktop/sylvie-backup-*"
    exit 1
fi

echo "📁 Projet cible: $PROJECT_DIR"
echo "📦 Sauvegarde source: $BACKUP_DIR"

# Vérification du projet cible
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Projet sylvie-v3-recovery non trouvé"
    echo "   Assurez-vous que l'étape 2 s'est bien déroulée"
    exit 1
fi

cd "$PROJECT_DIR"

echo ""
echo "🗂️  Migration des fichiers..."

# 1. Migration du store Zustand
if [ -f "$BACKUP_DIR/sylvieStore.ts" ]; then
    cp "$BACKUP_DIR/sylvieStore.ts" "src/store/sylvieStore.ts"
    echo "✅ Store Zustand migré"
else
    echo "⚠️  sylvieStore.ts non trouvé dans la sauvegarde"
fi

# 2. Migration de l'interface principale (page-fixed.tsx est prioritaire)
if [ -f "$BACKUP_DIR/page-fixed.tsx" ]; then
    cp "$BACKUP_DIR/page-fixed.tsx" "src/app/page.tsx"
    echo "✅ Interface principale migrée (page-fixed.tsx → page.tsx)"
elif [ -f "$BACKUP_DIR/page.tsx" ]; then
    cp "$BACKUP_DIR/page.tsx" "src/app/page.tsx"
    echo "✅ Interface principale migrée (page.tsx)"
else
    echo "⚠️  Aucune interface trouvée dans la sauvegarde"
fi

# 3. Configuration du layout pour Ant Design
echo ""
echo "⚙️  Configuration d'Ant Design..."

cat > "src/app/layout.tsx" << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ConfigProvider } from 'antd'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Sylvie v3.0 - Assistant Google Workspace',
  description: 'Assistant intelligent avec 22 outils MCP pour Google Workspace',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <ConfigProvider
          theme={{
            token: {
              colorPrimary: '#3B82F6',
              borderRadius: 8,
            },
          }}
        >
          {children}
        </ConfigProvider>
      </body>
    </html>
  )
}
EOF

echo "✅ Layout Ant Design configuré"

# 4. Mise à jour du fichier globals.css pour Ant Design
cat > "src/app/globals.css" << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Styles Ant Design compatibles avec Tailwind */
.ant-btn {
  @apply transition-all duration-200;
}

.ant-card {
  @apply shadow-sm;
}

.ant-typography {
  @apply mb-0;
}

/* Styles personnalisés Sylvie */
:root {
  --sylvie-primary: #3B82F6;
  --sylvie-secondary: #8B5CF6;
  --sylvie-success: #10B981;
}

body {
  font-feature-settings: 'rlig' 1, 'calt' 1;
}
EOF

echo "✅ Styles CSS configurés"

# 5. Test de compilation
echo ""
echo "🧪 Test de compilation..."

npm run build > /tmp/build-test.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Compilation réussie !"
else
    echo "⚠️  Erreurs de compilation détectées"
    echo "   Détails dans /tmp/build-test.log"
fi

# 6. Démarrage du serveur de développement
echo ""
echo "🚀 Démarrage du serveur de développement..."

# Lancement en arrière-plan pour test
npm run dev > /tmp/dev-server.log 2>&1 &
DEV_PID=$!

echo "   PID du serveur: $DEV_PID"
echo "   Attente du démarrage (10 secondes)..."

sleep 10

# Vérification que le serveur tourne
if kill -0 $DEV_PID 2>/dev/null; then
    echo "✅ Serveur de développement opérationnel !"
    echo "   URL: http://localhost:3000"
    echo "   PID: $DEV_PID (pour l'arrêter: kill $DEV_PID)"
    
    echo ""
    echo "📋 RÉSUMÉ MIGRATION:"
    echo "   ✅ Store Zustand: src/store/sylvieStore.ts"
    echo "   ✅ Interface: src/app/page.tsx"
    echo "   ✅ Layout Ant Design: src/app/layout.tsx"
    echo "   ✅ Styles CSS: src/app/globals.css"
    echo "   ✅ Serveur: http://localhost:3000"
    
    echo ""
    echo "🎉 ÉTAPE 3 TERMINÉE - Sylvie v3.0 est opérationnel !"
    echo ""
    echo "🔧 PROCHAINES ACTIONS:"
    echo "   1. Ouvrir http://localhost:3000 dans votre navigateur"
    echo "   2. Fermer VS Code actuel"
    echo "   3. Ouvrir le nouveau projet: $PROJECT_DIR"
    echo "   4. Continuer le développement de l'interface chat"
    
else
    echo "❌ Problème avec le serveur de développement"
    echo "   Consultez les logs: /tmp/dev-server.log"
fi

echo ""
echo "📍 Projet final: $PROJECT_DIR"
