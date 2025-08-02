# Services MCP Workspace - Sylvie v3

Ce dossier regroupe tous les modules/services pour chaque outil Google Workspace :
- Gmail
- Drive
- Docs
- Calendar
- Sheets
- Slides
- Forms
- Tasks
- Chat

## Structure
- Chaque service a son module Python (`__init__.py`) avec une fonction d’initialisation.
- Les decorators MCP (`mcp_decorators.py`) permettent l’injection et la gestion des scopes OAuth2.
- La gestion des tokens est centralisée (`token_manager.py`), support multi-comptes et refresh.
- Les scopes sont centralisés dans `scopes.py`.

## Prochaines étapes
- Implémenter la logique métier pour chaque service
- Ajouter la persistance et la sécurité des tokens
- Documenter chaque API et usage

## Sécurité & Persistance
- Les tokens OAuth2 sont stockés localement dans `tokens.json` (jamais commit)
- Chiffrement à prévoir pour la production
- Rotation et gestion multi-utilisateur recommandées
- Voir SECURITY.md pour les bonnes pratiques

## Documentation
- Voir DOCUMENTATION.md pour les exemples d’utilisation, gestion des tokens et ajout de nouveaux services
