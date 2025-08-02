# Sheets MCP Service - Sylvie v3
# Logique métier principale

from app.services.mcp_decorators import require_google_service
from app.services.scopes import SCOPES

@require_google_service('sheets', SCOPES['sheets'])
def list_spreadsheets(service, query=None, max_results=10):
    """
    Liste les spreadsheets Google Sheets selon une requête.
    Args:
        service: Service Sheets injecté
        query: Requête de recherche Sheets
        max_results: Nombre max de résultats
    Returns:
        Liste de spreadsheets (dict)
    """
    # TODO: Appel API Sheets, gestion pagination
    pass

@require_google_service('sheets', SCOPES['sheets'])
def get_spreadsheet(service, spreadsheet_id):
    """
    Récupère le contenu d’un spreadsheet par ID.
    Args:
        service: Service Sheets injecté
        spreadsheet_id: ID du spreadsheet
    Returns:
        Détail du spreadsheet (dict)
    """
    # TODO: Appel API Sheets, parsing contenu
    pass

# TODO: Ajouter update_spreadsheet, delete_spreadsheet, gestion cellules, batch
