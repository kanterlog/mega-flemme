from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/chat'
]

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=8000)

email = input('Entrez l\'email du compte Google authentifié : ')
token = {
    'access_token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri,
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'scopes': creds.scopes
}
try:
    with open('tokens.json', 'r') as f:
        tokens = json.load(f)
except FileNotFoundError:
    tokens = {}
tokens[email] = token
with open('tokens.json', 'w') as f:
    json.dump(tokens, f, indent=2)
print(f"Token généré et sauvegardé pour {email} dans tokens.json")
