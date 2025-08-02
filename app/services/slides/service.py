# Slides MCP Service - Sylvie v3
# Logique métier principale

from app.services.mcp_decorators import require_google_service
from app.services.scopes import SCOPES

@require_google_service('slides', SCOPES['slides'])
def list_presentations(service, query=None, max_results=10):
    """
    Liste les présentations Google Slides selon une requête.
    Args:
        service: Service Slides injecté
        query: Requête de recherche Slides
        max_results: Nombre max de résultats
    Returns:
        Liste de présentations (dict)
    """
    # TODO: Appel API Slides, gestion pagination
    pass

@require_google_service('slides', SCOPES['slides'])
def get_presentation(service, presentation_id):
    """
    Récupère le contenu d’une présentation par ID.
    Args:
        service: Service Slides injecté
        presentation_id: ID de la présentation
    Returns:
        Détail de la présentation (dict)
    """
    # TODO: Appel API Slides, parsing contenu
    pass

# TODO: Ajouter update_presentation, delete_presentation, gestion slides, batch
