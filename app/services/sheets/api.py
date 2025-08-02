# API Métier Sheets MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class SheetsAPI:
    def __init__(self, account_email):
        self.token_manager = TokenManagerStorage()
        self.token = self.token_manager.get_token(account_email)
        self.service = self._get_service()


    def _get_service(self):
        from google.oauth2.credentials import Credentials
        if not self.token:
            raise Exception('Token OAuth2 manquant pour ce compte')
        creds = Credentials(
            token=self.token.get('access_token'),
            refresh_token=self.token.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=self.token.get('client_id'),
            client_secret=self.token.get('client_secret'),
            scopes=SCOPES['sheets']
        )
        return build('sheets', 'v4', credentials=creds)


    def list_spreadsheets(self, query=None, max_results=10):
        # Google Sheets API n'a pas de méthode list native, il faut passer par Drive
        # Utiliser DriveAPI pour lister les fichiers de type spreadsheet
        return []


    def get_spreadsheet(self, spreadsheet_id):
        try:
            sheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            return sheet
        except Exception as e:
            print(f"Erreur get_spreadsheet: {e}")
            return None


    def create_spreadsheet(self, spreadsheet_body):
        """
        Crée un spreadsheet Google Sheets.
        """
        try:
            result = self.service.spreadsheets().create(body=spreadsheet_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_spreadsheet: {e}")
            return None

    def update_spreadsheet(self, spreadsheet_id, requests):
        """
        Met à jour le contenu d’un spreadsheet Google Sheets.
        """
        try:
            result = self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()
            return result
        except Exception as e:
            print(f"Erreur update_spreadsheet: {e}")
            return None

    def batch_get_spreadsheets(self, spreadsheet_ids):
        """
        Récupère plusieurs spreadsheets Google Sheets en batch.
        """
        results = []
        for sid in spreadsheet_ids:
            try:
                sheet = self.get_spreadsheet(sid)
                results.append(sheet)
            except Exception as e:
                print(f"Erreur batch_get_spreadsheets (id={sid}): {e}")
                results.append(None)
        return results
