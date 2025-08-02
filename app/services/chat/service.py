# Chat MCP Service - Sylvie v3
# Logique métier principale

from app.services.mcp_decorators import require_google_service
from app.services.scopes import SCOPES

@require_google_service('chat', SCOPES['chat'])
def list_spaces(service, max_results=10):
    """
    Liste les espaces Google Chat.
    Args:
        service: Service Chat injecté
        max_results: Nombre max de résultats
    Returns:
        Liste d’espaces (dict)
    """
    # TODO: Appel API Chat, gestion pagination
    pass

@require_google_service('chat', SCOPES['chat'])
def get_space(service, space_id):
    """
    Récupère le détail d’un espace Chat par ID.
    Args:
        service: Service Chat injecté
        space_id: ID de l’espace
    Returns:
        Détail de l’espace (dict)
    """
    # TODO: Appel API Chat, parsing contenu
    pass

# TODO: Ajouter send_message, search_messages, gestion membres, batch
