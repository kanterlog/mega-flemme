# API Métier Drive MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class DriveAPI:
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
            scopes=SCOPES['drive']
        )
        return build('drive', 'v3', credentials=creds)


    def list_files(self, query=None, max_results=10):
        try:
            results = self.service.files().list(q=query, pageSize=max_results).execute()
            return results.get('files', [])
        except Exception as e:
            print(f"Erreur list_files: {e}")
            return []


    def get_file(self, file_id):
        try:
            file = self.service.files().get(fileId=file_id).execute()
            return file
        except Exception as e:
            print(f"Erreur get_file: {e}")
            return None


    def create_file(self, file_metadata, media_body=None):
        """
        Crée un fichier Drive.
        """
        try:
            result = self.service.files().create(body=file_metadata, media_body=media_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_file: {e}")
            return None

    def update_file(self, file_id, file_metadata):
        """
        Met à jour les métadonnées d’un fichier Drive.
        """
        try:
            result = self.service.files().update(fileId=file_id, body=file_metadata).execute()
            return result
        except Exception as e:
            print(f"Erreur update_file: {e}")
            return None

    def batch_get_files(self, file_ids):
        """
        Récupère plusieurs fichiers Drive en batch.
        """
        results = []
        for fid in file_ids:
            try:
                file = self.get_file(fid)
                results.append(file)
            except Exception as e:
                print(f"Erreur batch_get_files (id={fid}): {e}")
                results.append(None)
        return results
