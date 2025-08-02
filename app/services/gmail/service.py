# Gmail MCP Service - Sylvie v3
# Logique métier principale

from app.services.mcp_decorators import require_google_service
from app.services.scopes import SCOPES

@require_google_service('gmail', SCOPES['gmail'])
def list_messages(service, query=None, max_results=10):
    """
    Liste les messages Gmail selon une requête (search).
    Args:
        service: Service Gmail injecté
        query: Requête de recherche Gmail (ex: 'is:unread')
        max_results: Nombre max de résultats
    Returns:
        Liste de messages (dict)
    """
    # TODO: Appel API Gmail, gestion pagination
    pass

@require_google_service('gmail', SCOPES['gmail'])
def get_message(service, message_id):
    """
    Récupère le contenu complet d’un message Gmail par ID.
    Args:
        service: Service Gmail injecté
        message_id: ID du message
    Returns:
        Détail du message (dict)
    """
    # TODO: Appel API Gmail, parsing contenu
    pass

# TODO: Ajouter send_message, create_draft, delete_message, batch, pièces jointes, labels
