# API Métier Chat MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class ChatAPI:
    def __init__(self, account_email):
        self.token_manager = TokenManagerStorage()

    def send_message(self, space_id, message_body):
        """
        Envoie un message dans un espace Google Chat.
        """
        try:
            result = self.service.spaces().messages().create(parent=f'spaces/{space_id}', body=message_body).execute()
            return result
        except Exception as e:
            print(f"Erreur send_message: {e}")
            return None
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
            scopes=SCOPES['chat']
        )
        return build('chat', 'v1', credentials=creds)


    def list_spaces(self, max_results=10):
        results = self.service.spaces().list(pageSize=max_results).execute()
        return results.get('spaces', [])


    def get_space(self, space_id):
        try:
            space = self.service.spaces().get(spaceId=space_id).execute()
            return space
        except Exception as e:
            print(f"Erreur get_space: {e}")
            return None


    def create_space(self, space_body):
        """
        Crée un espace Google Chat.
        """
        try:
            result = self.service.spaces().create(body=space_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_space: {e}")
            return None

    def update_space(self, space_id, space_body):
        """
        Met à jour un espace Google Chat.
        """
        try:
            result = self.service.spaces().update(spaceId=space_id, body=space_body).execute()
            return result
        except Exception as e:
            print(f"Erreur update_space: {e}")
            return None

    def batch_get_spaces(self, space_ids):
        """
        Récupère plusieurs espaces Google Chat en batch.
        """
        results = []
        for sid in space_ids:
            try:
                space = self.get_space(sid)
                results.append(space)
            except Exception as e:
                print(f"Erreur batch_get_spaces (id={sid}): {e}")
                results.append(None)
        return results
