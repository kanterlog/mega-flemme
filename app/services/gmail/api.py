# API Métier Gmail MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class GmailAPI:
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
            scopes=SCOPES['gmail']
        )
        return build('gmail', 'v1', credentials=creds)


    def list_messages(self, query=None, max_results=10):
        results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        try:
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            return results.get('messages', [])
        except Exception as e:
            print(f"Erreur list_messages: {e}")
            return []


    def get_message(self, message_id):
        msg = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        try:
            msg = self.service.users().messages().get(userId='me', id=message_id).execute()
            return msg
        except Exception as e:
            print(f"Erreur get_message: {e}")
            return None


    def send_message(self, raw_message):
        """
        Envoie un message Gmail (format RFC822 base64).
        """
        message = {'raw': raw_message}
        try:
            message = {'raw': raw_message}
            result = self.service.users().messages().send(userId='me', body=message).execute()
            return result
        except Exception as e:
            print(f"Erreur send_message: {e}")
            return None

    def create_draft(self, raw_message):
        """
        Crée un brouillon Gmail (format RFC822 base64).
        """
        draft = {'message': {'raw': raw_message}}
        try:
            draft = {'message': {'raw': raw_message}}
            result = self.service.users().drafts().create(userId='me', body=draft).execute()
            return result
        except Exception as e:
            print(f"Erreur create_draft: {e}")
            return None

    def batch_get_messages(self, message_ids):
        """
        Récupère plusieurs messages Gmail en batch.
        """
        results = []
        for mid in message_ids:
            try:
                msg = self.get_message(mid)
                results.append(msg)
            except Exception as e:
                print(f"Erreur batch_get_messages (id={mid}): {e}")
                results.append(None)
        return results
