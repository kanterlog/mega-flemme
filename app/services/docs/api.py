# API Métier Docs MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class DocsAPI:
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
            scopes=SCOPES['docs']
        )
        return build('docs', 'v1', credentials=creds)


    def list_docs(self, query=None, max_results=10):
        # Google Docs API n'a pas de méthode list native, il faut passer par Drive
        # Utiliser DriveAPI pour lister les fichiers de type document
        return []


    def get_doc(self, doc_id):
        try:
            doc = self.service.documents().get(documentId=doc_id).execute()
            return doc
        except Exception as e:
            print(f"Erreur get_doc: {e}")
            return None


    def create_doc(self, title):
        """
        Crée un document Google Docs.
        """
        try:
            doc = {'title': title}
            result = self.service.documents().create(body=doc).execute()
            return result
        except Exception as e:
            print(f"Erreur create_doc: {e}")
            return None

    def update_doc(self, doc_id, requests):
        """
        Met à jour le contenu d’un document Google Docs.
        """
        try:
            result = self.service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
            return result
        except Exception as e:
            print(f"Erreur update_doc: {e}")
            return None

    def batch_get_docs(self, doc_ids):
        """
        Récupère plusieurs documents Google Docs en batch.
        """
        results = []
        for did in doc_ids:
            try:
                doc = self.get_doc(did)
                results.append(doc)
            except Exception as e:
                print(f"Erreur batch_get_docs (id={did}): {e}")
                results.append(None)
        return results
