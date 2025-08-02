# Sécurité des Tokens OAuth2 - Sylvie v3 MCP

## Bonnes pratiques
- Les tokens OAuth2 sont stockés localement dans `tokens.json` (jamais commit dans Git)
- Prévoir chiffrement des tokens pour la production
- Rotation régulière des tokens recommandée
- .gitignore doit inclure tous les fichiers de credentials et tokens
- Ne jamais exposer les tokens dans les logs ou l’UI
- Utiliser des scopes minimaux pour chaque service
- Support multi-utilisateur et multi-comptes à prévoir

## TODO
- Implémenter chiffrement des tokens
- Ajouter gestion de rotation et révocation
- Documenter la procédure de récupération et de backup
