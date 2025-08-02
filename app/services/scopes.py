# Scopes Google Workspace MCP
# Centralisation des scopes par service

SCOPES = {
    'gmail': ['https://mail.google.com/'],
    'drive': ['https://www.googleapis.com/auth/drive'],
    'docs': ['https://www.googleapis.com/auth/documents'],
    'calendar': ['https://www.googleapis.com/auth/calendar'],
    'sheets': ['https://www.googleapis.com/auth/spreadsheets'],
    'slides': ['https://www.googleapis.com/auth/presentations'],
    'forms': ['https://www.googleapis.com/auth/forms'],
    'tasks': ['https://www.googleapis.com/auth/tasks'],
    'chat': ['https://www.googleapis.com/auth/chat'],
}

# TODO: Ajouter gestion dynamique des scopes, validation
