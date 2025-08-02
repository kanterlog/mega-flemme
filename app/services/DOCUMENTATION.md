# Documentation MCP Workspace - Sylvie v3

## Structure des services
- Chaque service (Gmail, Drive, Docs, Calendar, Sheets, Slides, Forms, Tasks, Chat) dispose d’un module métier avec decorators, scopes et gestion des tokens.

## Exemple d’utilisation (Gmail)
```python
from app.services.gmail.service import list_messages, get_message

# Listing des messages
messages = list_messages(service, query='is:unread', max_results=5)

# Récupération d’un message
msg = get_message(service, message_id='1234567890')
```

## Gestion des tokens
```python
from app.services.token_manager_storage import TokenManagerStorage

manager = TokenManagerStorage()
token = manager.get_token('user@gmail.com')
manager.set_token('user@gmail.com', token)
```

## Ajout d’un nouveau service
- Créer le dossier et le module métier
- Définir les scopes dans `scopes.py`
- Utiliser le decorator `require_google_service`
- Documenter les fonctions principales dans le README du service
