class TasksAPI:
    def __init__(self, account_email):
        self.token_manager = TokenManagerStorage()

    def create_task(self, task_list_id, task_body):
        """
        Crée une tâche dans une liste Google Tasks.
        """
        try:
            result = self.service.tasks().insert(tasklist=task_list_id, body=task_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_task: {e}")
            return None
    def update_task(self, task_list_id, task_id, task_body):
        """
        Met à jour une tâche dans une liste Google Tasks.
        """
        try:
            result = self.service.tasks().update(tasklist=task_list_id, task=task_id, body=task_body).execute()
            return result
        except Exception as e:
            print(f"Erreur update_task: {e}")
            return None
    
    def batch_get_tasks(self, task_list_id, task_ids):
        """
        Récupère plusieurs tâches en batch.
        """
        results = []
        for tid in task_ids:
            try:
                task = self.service.tasks().get(tasklist=task_list_id, task=tid).execute()
                results.append(task)
            except Exception as e:
                print(f"Erreur batch_get_tasks (id={tid}): {e}")
                results.append(None)
        return results
    def update_task(self, task_list_id, task_id, task_body):
        """
        Met à jour une tâche dans une liste Google Tasks.
        """
        try:
            result = self.service.tasks().update(tasklist=task_list_id, task=task_id, body=task_body).execute()
            return result
        except Exception as e:
            print(f"Erreur update_task: {e}")
            return None
    
    def batch_get_tasks(self, task_list_id, task_ids):
        """
        Récupère plusieurs tâches en batch.
        """
        results = []
        for tid in task_ids:
            try:
                task = self.service.tasks().get(tasklist=task_list_id, task=tid).execute()
                results.append(task)
            except Exception as e:
                print(f"Erreur batch_get_tasks (id={tid}): {e}")
                results.append(None)
        return results

    def update_task(self, task_list_id, task_id, task_body):
        """
        Met à jour une tâche dans une liste Google Tasks.
        """
        try:
            result = self.service.tasks().update(tasklist=task_list_id, task=task_id, body=task_body).execute()
            return result
        except Exception as e:
            print(f"Erreur update_task: {e}")
            return None

    def batch_get_tasks(self, task_list_id, task_ids):
        """
        Récupère plusieurs tâches en batch.
        """
        results = []
        for tid in task_ids:
            try:
                task = self.service.tasks().get(tasklist=task_list_id, task=tid).execute()
                results.append(task)
            except Exception as e:
                print(f"Erreur batch_get_tasks (id={tid}): {e}")
                results.append(None)
        return results
# API Métier Tasks MCP - Sylvie v3
# Implémentation concrète (exemple avec google-api-python-client)

from googleapiclient.discovery import build
from app.services.token_manager_storage import TokenManagerStorage
from app.services.scopes import SCOPES

class TasksAPI:
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
            scopes=SCOPES['tasks']
        )
        return build('tasks', 'v1', credentials=creds)


    def list_task_lists(self, max_results=10):
        results = self.service.tasklists().list(maxResults=max_results).execute()
        return results.get('items', [])


    def get_task_list(self, task_list_id):
        tasklist = self.service.tasklists().get(tasklist=task_list_id).execute()
        return tasklist


    def create_task_list(self, task_list_body):
        """
        Crée une liste de tâches Google Tasks.
        """
        try:
            result = self.service.tasklists().insert(body=task_list_body).execute()
            return result
        except Exception as e:
            print(f"Erreur create_task_list: {e}")
            return None

    def update_task_list(self, task_list_id, task_list_body):
        """
        Met à jour une liste de tâches Google Tasks.
        """
        try:
            result = self.service.tasklists().update(tasklist=task_list_id, body=task_list_body).execute()
            return result
        except Exception as e:
            print(f"Erreur update_task_list: {e}")
            return None

    def batch_get_task_lists(self, task_list_ids):
        """
        Récupère plusieurs listes de tâches Google Tasks en batch.
        """
        results = []
        for tid in task_list_ids:
            try:
                tasklist = self.get_task_list(tid)
                results.append(tasklist)
            except Exception as e:
                print(f"Erreur batch_get_task_lists (id={tid}): {e}")
                results.append(None)
        return results
