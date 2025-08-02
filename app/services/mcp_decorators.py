# MCP Decorators pour injection de services et gestion des scopes
# Inspiré Workspace MCP

from functools import wraps

def require_google_service(service_name, scopes):
    """
    Decorator pour injecter le service Google et vérifier les scopes OAuth2.
    Usage : @require_google_service('gmail', ['https://mail.google.com/'])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: Vérifier token, scopes, injecter le service
            # service = get_service(service_name, scopes)
            # return func(service, *args, **kwargs)
            pass
        return wrapper
    return decorator

# TODO: Ajouter gestion centralisée des tokens, refresh, multi-comptes
