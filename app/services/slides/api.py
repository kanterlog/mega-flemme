# API Métier Slides MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class SlidesAPI:
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
            scopes=SCOPES['slides']
        )
        return build('slides', 'v1', credentials=creds)


    def list_presentations(self, query=None, max_results=10):
        # Google Slides API n'a pas de méthode list native, il faut passer par Drive
        # Utiliser DriveAPI pour lister les fichiers de type presentation
        return []


    def get_presentation(self, presentation_id):
        try:
            pres = self.service.presentations().get(presentationId=presentation_id).execute()
            return pres
        except Exception as e:
            print(f"Erreur get_presentation: {e}")
            return None


    def create_presentation(self, presentation_body):
        """
        Crée une présentation Google Slides.
        """
        try:
            result = self.service.presentations().create(body=presentation_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_presentation: {e}")
            return None

    def update_presentation(self, presentation_id, requests):
        """
        Met à jour le contenu d’une présentation Google Slides.
        """
        try:
            result = self.service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': requests}).execute()
            return result
        except Exception as e:
            print(f"Erreur update_presentation: {e}")
            return None

    def batch_get_presentations(self, presentation_ids):
        """
        Récupère plusieurs présentations Google Slides en batch.
        """
        results = []
        for pid in presentation_ids:
            try:
                pres = self.get_presentation(pid)
                results.append(pres)
            except Exception as e:
                print(f"Erreur batch_get_presentations (id={pid}): {e}")
                results.append(None)
        return results
