# Forms MCP Service - Sylvie v3
# Logique métier principale

from app.services.mcp_decorators import require_google_service
from app.services.scopes import SCOPES

@require_google_service('forms', SCOPES['forms'])
def list_forms(service, query=None, max_results=10):
    """
    Liste les Google Forms selon une requête.
    Args:
        service: Service Forms injecté
        query: Requête de recherche Forms
        max_results: Nombre max de résultats
    Returns:
        Liste de forms (dict)
    """
    # TODO: Appel API Forms, gestion pagination
    pass

@require_google_service('forms', SCOPES['forms'])
def get_form(service, form_id):
    """
    Récupère le contenu d’un Google Form par ID.
    Args:
        service: Service Forms injecté
        form_id: ID du form
    Returns:
        Détail du form (dict)
    """
    # TODO: Appel API Forms, parsing contenu
    pass

# TODO: Ajouter create_form, update_form, delete_form, gestion réponses, batch
