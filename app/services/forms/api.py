# API Métier Forms MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class FormsAPI:
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
            scopes=SCOPES['forms']
        )
        return build('forms', 'v1', credentials=creds)


    def list_forms(self, query=None, max_results=10):
        # Google Forms API n'a pas de méthode list native, il faut passer par Drive
        # Utiliser DriveAPI pour lister les fichiers de type form
        return []


    def get_form(self, form_id):
        try:
            form = self.service.forms().get(formId=form_id).execute()
            return form
        except Exception as e:
            print(f"Erreur get_form: {e}")
            return None


    def create_form(self, form_body):
        """
        Crée un Google Form.
        """
        try:
            result = self.service.forms().create(body=form_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_form: {e}")
            return None

    def update_form(self, form_id, requests):
        """
        Met à jour le contenu d’un Google Form.
        """
        try:
            result = self.service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
            return result
        except Exception as e:
            print(f"Erreur update_form: {e}")
            return None

    def batch_get_forms(self, form_ids):
        """
        Récupère plusieurs Google Forms en batch.
        """
        results = []
        for fid in form_ids:
            try:
                form = self.get_form(fid)
                results.append(form)
            except Exception as e:
                print(f"Erreur batch_get_forms (id={fid}): {e}")
                results.append(None)
        return results
