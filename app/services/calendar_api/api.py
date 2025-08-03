# API Métier Calendar MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class CalendarAPI:
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
            scopes=SCOPES['calendar']
        )
        return build('calendar', 'v3', credentials=creds)


    def list_events(self, calendar_id='primary', time_min=None, time_max=None, max_results=10):
        try:
            results = self.service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max, maxResults=max_results).execute()
            return results.get('items', [])
        except Exception as e:
            print(f"Erreur list_events: {e}")
            return []


    def get_event(self, calendar_id, event_id):
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            return event
        except Exception as e:
            print(f"Erreur get_event: {e}")
            return None


    def create_event(self, calendar_id, event_body):
        """
        Crée un événement Google Calendar.
        """
        try:
            result = self.service.events().insert(calendarId=calendar_id, body=event_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_event: {e}")
            return None

    def update_event(self, calendar_id, event_id, event_body):
        """
        Met à jour un événement Google Calendar.
        """
        try:
            result = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event_body).execute()
            return result
        except Exception as e:
            print(f"Erreur update_event: {e}")
            return None

    def batch_get_events(self, calendar_id, event_ids):
        """
        Récupère plusieurs événements Google Calendar en batch.
        """
        results = []
        for eid in event_ids:
            try:
                event = self.get_event(calendar_id, eid)
                results.append(event)
            except Exception as e:
                print(f"Erreur batch_get_events (id={eid}): {e}")
                results.append(None)
        return results
