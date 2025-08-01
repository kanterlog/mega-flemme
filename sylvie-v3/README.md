# Sylvie v3.0 - Assistant IA Google Workspace 🤖✨

> **Assistant IA révolutionnaire pour Google Workspace, inspiré par LobeChat avec une architecture Next.js 15 moderne**

![Sylvie v3.0](https://img.shields.io/badge/Sylvie-v3.0-8b5cf6?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-15.3.5-black?style=for-the-badge&logo=next.js)
![React](https://img.shields.io/badge/React-19.1.0-61dafb?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8.4-blue?style=for-the-badge&logo=typescript)
![Ant Design](https://img.shields.io/badge/Ant%20Design-5.26.6-1890ff?style=for-the-badge&logo=antdesign)

## 🌟 Fonctionnalités Révolutionnaires

### 💎 Interface Moderne Inspirée de LobeChat
- **Interface conversationnelle fluide** avec animations Framer Motion
- **Conversations avec branches** pour explorer différents scénarios
- **Visualisation chain-of-thought** pour comprendre le raisonnement de l'IA
- **Thème adaptatif** clair/sombre avec design glassmorphism

### 🚀 Intégration Google Workspace Complète
- **Gmail** : Gestion avancée des emails, recherche intelligente, rédaction assistée
- **Calendar** : Planification automatique, gestion des conflits, suggestions intelligentes
- **Drive** : Organisation automatique, recherche sémantique, partage intelligent
- **Docs/Sheets/Slides** : Création collaborative, templates intelligents, analyse de données
- **Tasks** : Gestion de projets avec IA, priorisation automatique

### 🔌 Architecture MCP (Model Context Protocol)
- **Serveurs MCP modulaires** pour chaque service Google
- **Marketplace de plugins** pour étendre les capacités
- **Support multi-fournisseurs IA** : OpenAI, Anthropic, Google AI, etc.
- **Cache intelligent** avec TTL configurable pour optimiser les performances

### 🎯 Capacités IA Avancées
- **Analyse contextuelle** des documents et emails
- **Suggestions proactives** basées sur les habitudes
- **Automatisation workflow** avec validation humaine
- **Synthèse intelligente** des réunions et documents

## 🏗️ Architecture Technique

### Stack Technologique
```
Frontend     : Next.js 15 + React 19 + TypeScript
UI Framework : Ant Design + Tailwind CSS + Framer Motion
State        : Zustand + React Query
Auth         : NextAuth.js + Google OAuth2
Backend      : Next.js API Routes + MCP SDK
Database     : PostgreSQL + Drizzle ORM
Cache        : Redis (optionnel)
Deploy       : Vercel + Docker
```

### Structure du Projet
```
sylvie-v3/
├── src/
│   ├── app/                 # App Router Next.js 15
│   ├── components/          # Composants UI réutilisables
│   ├── features/           # Fonctionnalités métier
│   ├── services/           # Services et API
│   ├── store/              # État global Zustand
│   ├── types/              # Types TypeScript
│   ├── utils/              # Utilitaires
│   └── styles/             # Styles globaux
├── mcp-server/             # Serveur MCP autonome
├── docs/                   # Documentation
└── scripts/                # Scripts de déploiement
```

## 🚦 Démarrage Rapide

### Prérequis
- Node.js 18+ 
- npm ou yarn
- Compte Google Cloud avec APIs activées
- PostgreSQL (optionnel pour la persistance)

### Installation

1. **Cloner et installer les dépendances**
```bash
git clone <repository-url>
cd sylvie-v3
npm install
```

2. **Configuration environnement**
```bash
cp .env.example .env.local
# Éditer .env.local avec vos clés API
```

3. **Variables d'environnement essentielles**
```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3010
```

4. **Démarrer le serveur de développement**
```bash
npm run dev
```

5. **Accéder à l'application**
```
http://localhost:3010
```

## 🔧 Configuration Avancée

### Configuration Google Cloud

1. **Créer un projet Google Cloud**
2. **Activer les APIs nécessaires** :
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - Google Slides API
   - Google Tasks API

3. **Configurer OAuth 2.0** :
   - Créer des identifiants OAuth 2.0
   - Ajouter `http://localhost:3010/api/auth/callback/google` aux URI de redirection

### Base de Données (Optionnel)

```bash
# Générer les migrations
npm run db:generate

# Appliquer les migrations
npm run db:migrate

# Interface d'administration
npm run db:studio
```

## 📋 Scripts Disponibles

| Script | Description |
|--------|-------------|
| `npm run dev` | Serveur de développement avec Turbopack |
| `npm run build` | Build de production |
| `npm run start` | Serveur de production |
| `npm run type-check` | Vérification TypeScript |
| `npm run lint` | Linting et correction automatique |
| `npm run test` | Tests unitaires |
| `npm run test:watch` | Tests en mode watch |

## 🎨 Personnalisation

### Thème et Styles
- Modifier `src/styles/globals.css` pour les styles globaux
- Personnaliser `tailwind.config.js` pour les couleurs et animations
- Adapter la configuration Ant Design dans `src/app/layout.tsx`

### Intégrations IA
- Ajouter de nouveaux fournisseurs dans `src/services/ai/`
- Configurer les modèles dans `src/store/sylvieStore.ts`
- Étendre les capacités MCP dans `mcp-server/`

## 📚 Documentation Complète

### Guides de Développement
- [Architecture MCP](./docs/mcp-architecture.md)
- [Guide des Composants](./docs/components-guide.md)
- [Intégration Google APIs](./docs/google-apis.md)
- [Déploiement Production](./docs/deployment.md)

### Références API
- [API Routes](./docs/api-reference.md)
- [Hooks et Stores](./docs/hooks-stores.md)
- [Types TypeScript](./docs/types-reference.md)

## 🚀 Roadmap v3.0

### Phase 1 : Fondations (Semaines 1-2) ✅
- [x] Architecture Next.js 15 + React 19
- [x] Interface utilisateur avec Ant Design
- [x] Système d'état avec Zustand
- [x] Authentification Google OAuth2

### Phase 2 : Intégrations (Semaines 3-4) 🔄
- [ ] Serveur MCP Google Workspace
- [ ] Intégration Gmail complète
- [ ] Intégration Calendar et Drive
- [ ] Cache intelligent avec Redis

### Phase 3 : IA Avancée (Semaines 5-6) 📋
- [ ] Support multi-fournisseurs IA
- [ ] Conversations avec branches
- [ ] Chain-of-thought visualization
- [ ] Automatisation workflow

### Phase 4 : Production (Semaines 7-8) 📋
- [ ] Application desktop Electron
- [ ] Marketplace de plugins MCP
- [ ] Déploiement production
- [ ] Monitoring et analytics

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **[LobeChat](https://github.com/lobehub/lobe-chat)** pour l'inspiration architecturale
- **[Model Context Protocol](https://modelcontextprotocol.io/)** pour le standard MCP
- **Équipe Next.js** pour le framework révolutionnaire
- **Communauté Ant Design** pour les composants excellents

## 📞 Support

- 📧 Email : support@sylvie.ai
- 🐛 Issues : [GitHub Issues](../../issues)
- 💬 Discussions : [GitHub Discussions](../../discussions)
- 📖 Documentation : [docs.sylvie.ai](https://docs.sylvie.ai)

---

<div align="center">

**Créé avec ❤️ par l'équipe Sylvie**

[🌐 Website](https://sylvie.ai) • [📚 Docs](https://docs.sylvie.ai) • [🐦 Twitter](https://twitter.com/sylvieai) • [💼 LinkedIn](https://linkedin.com/company/sylvie-ai)

</div>
