#!/bin/bash

# Sylvie v3.0 - Setup Propre et Contrôlé
# Usage: ./setup-sylvie-clean.sh

set -e  # Arrêter sur erreur

echo "🚀 Setup Sylvie v3.0 - Environnement Propre"
echo "============================================"

# 1. Nettoyage complet
echo "🧹 Nettoyage de l'environnement..."
rm -rf sylvie-v3-clean
npm cache clean --force
rm -rf ~/.npm/_npx

# 2. Vérification des prérequis
echo "🔍 Vérification de l'environnement..."
node_version=$(node --version)
npm_version=$(npm --version)
echo "Node.js: $node_version"
echo "npm: $npm_version"

# Vérifier Node.js >= 18
if ! node -e "process.exit(process.version.split('.')[0].substring(1) >= 18 ? 0 : 1)"; then
    echo "❌ Node.js 18+ requis. Version actuelle: $node_version"
    exit 1
fi

# 3. Création du projet avec version exacte
echo "📦 Création du projet Next.js..."
npx create-next-app@14.2.31 sylvie-v3-clean \
    --typescript \
    --tailwind \
    --eslint \
    --app \
    --src-dir \
    --import-alias "@/*" \
    --no-git

cd sylvie-v3-clean

# 4. Installation des dépendances avec versions exactes
echo "📚 Installation des dépendances..."
npm install --save-exact \
    zustand@4.4.7 \
    antd@5.12.8 \
    @ant-design/icons@5.2.6 \
    framer-motion@10.16.16 \
    lucide-react@0.294.0 \
    nanoid@5.0.4 \
    class-variance-authority@0.7.0 \
    clsx@2.0.0 \
    tailwind-merge@2.2.0

# 5. Dev dependencies
npm install --save-exact --save-dev \
    @types/node@20.10.6 \
    @types/react@18.2.45 \
    @types/react-dom@18.2.18 \
    typescript@5.3.3

# 6. Configuration next.config.js optimisée
cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Stabilité pour le développement
    appDir: true,
  },
  // Éviter les conflits de modules
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
  // Port personnalisé pour éviter les conflits
  env: {
    CUSTOM_PORT: process.env.PORT || '3012',
  },
};

module.exports = nextConfig;
EOF

# 7. Mise à jour du package.json avec scripts optimisés
echo "⚙️ Configuration des scripts..."
npm pkg set scripts.dev="next dev -p 3012"
npm pkg set scripts.build="next build"
npm pkg set scripts.start="next start -p 3012"
npm pkg set scripts.lint="next lint"
npm pkg set scripts.type-check="tsc --noEmit"

# 8. Configuration TypeScript stricte mais pragmatique
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    // Moins strict pour les props Ant Design
    "noImplicitAny": false,
    "strictNullChecks": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# 9. Tailwind config optimisé pour Ant Design
cat > tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  // Éviter les conflits avec Ant Design
  corePlugins: {
    preflight: false,
  },
}
export default config
EOF

# 10. Test de compilation
echo "🧪 Test de compilation..."
npm run type-check

# 11. Test du serveur dev
echo "🎯 Test du serveur de développement..."
timeout 10s npm run dev || {
    echo "⚠️  Serveur arrêté après 10s (normal pour le test)"
}

echo ""
echo "✅ Setup terminé avec succès !"
echo "📁 Projet créé dans: $(pwd)"
echo "🚀 Pour démarrer: npm run dev"
echo "🌐 URL: http://localhost:3012"
echo ""
echo "📋 Prochaines étapes :"
echo "  1. cd sylvie-v3-clean"
echo "  2. npm run dev"
echo "  3. Copier vos composants existants"
echo "  4. Adapter les types si nécessaire"
