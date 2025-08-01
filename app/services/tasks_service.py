"""
✅ Service Tasks pour Sylvie
Phase 3.10 - Intégration Google Tasks

Gestion complète des tâches Google Tasks pour KanterMator
"""

import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class TasksService:
    """Service de gestion des tâches Google Tasks"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.tasks_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Tasks est initialisé"""
        if self.tasks_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.tasks_service = build('tasks', 'v1', credentials=credentials)
                logger.info("✅ Service Tasks initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Tasks", error=str(e))
                raise
    
    async def get_tasks(self, completed: bool = False, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère les tâches
        
        Args:
            completed: Inclure les tâches terminées
            max_results: Nombre maximum de tâches
            
        Returns:
            Liste des tâches
        """
        await self._ensure_service_initialized()
        
        try:
            # Récupération de la liste principale des tâches
            tasklists = self.tasks_service.tasklists().list().execute()
            if not tasklists.get('items'):
                return []
            
            main_tasklist = tasklists['items'][0]['id']
            
            # Récupération des tâches
            show_completed = 'true' if completed else 'false'
            tasks_result = self.tasks_service.tasks().list(
                tasklist=main_tasklist,
                maxResults=max_results,
                showCompleted=show_completed,
                showHidden=False
            ).execute()
            
            tasks = tasks_result.get('items', [])
            
            parsed_tasks = []
            for task in tasks:
                parsed_tasks.append({
                    'id': task['id'],
                    'title': task.get('title', 'Tâche sans titre'),
                    'notes': task.get('notes', ''),
                    'status': task.get('status', 'needsAction'),
                    'due': task.get('due', ''),
                    'updated': task.get('updated', ''),
                    'completed': task.get('completed', ''),
                    'parent': task.get('parent', ''),
                    'position': task.get('position', ''),
                    'links': task.get('links', [])
                })
            
            logger.info("✅ Tâches récupérées", count=len(parsed_tasks))
            return parsed_tasks
            
        except HttpError as e:
            logger.error("❌ Erreur API Tasks", error=str(e))
            return []
        except Exception as e:
            logger.error("❌ Erreur inattendue Tasks", error=str(e))
            return []
    
    async def create_task(self, title: str, notes: str = "", due_date: Optional[datetime] = None) -> bool:
        """
        Crée une nouvelle tâche
        
        Args:
            title: Titre de la tâche
            notes: Notes optionnelles
            due_date: Date d'échéance optionnelle
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            # Récupération de la liste principale
            tasklists = self.tasks_service.tasklists().list().execute()
            if not tasklists.get('items'):
                return False
            
            main_tasklist = tasklists['items'][0]['id']
            
            # Construction de la tâche
            task = {
                'title': title,
                'notes': notes
            }
            
            if due_date:
                task['due'] = due_date.isoformat() + 'Z'
            
            # Création de la tâche
            created_task = self.tasks_service.tasks().insert(
                tasklist=main_tasklist,
                body=task
            ).execute()
            
            logger.info("✅ Tâche créée", title=title, task_id=created_task['id'])
            return True
            
        except Exception as e:
            logger.error("❌ Erreur création tâche", error=str(e))
            return False
    
    async def complete_task(self, task_id: str) -> bool:
        """
        Marque une tâche comme terminée
        
        Args:
            task_id: ID de la tâche
            
        Returns:
            True si succès, False sinon
        """
        await self._ensure_service_initialized()
        
        try:
            # Récupération de la liste principale
            tasklists = self.tasks_service.tasklists().list().execute()
            if not tasklists.get('items'):
                return False
            
            main_tasklist = tasklists['items'][0]['id']
            
            # Mise à jour de la tâche
            task = {
                'id': task_id,
                'status': 'completed'
            }
            
            self.tasks_service.tasks().update(
                tasklist=main_tasklist,
                task=task_id,
                body=task
            ).execute()
            
            logger.info("✅ Tâche terminée", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur complétion tâche", error=str(e))
            return False
    
    async def delete_task(self, task_id: str) -> bool:
        """Supprime une tâche"""
        await self._ensure_service_initialized()
        
        try:
            tasklists = self.tasks_service.tasklists().list().execute()
            if not tasklists.get('items'):
                return False
            
            main_tasklist = tasklists['items'][0]['id']
            
            self.tasks_service.tasks().delete(
                tasklist=main_tasklist,
                task=task_id
            ).execute()
            
            logger.info("✅ Tâche supprimée", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("❌ Erreur suppression tâche", error=str(e))
            return False
    
    async def get_tasks_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé des tâches pour Sylvie"""
        try:
            all_tasks = await self.get_tasks(completed=False, max_results=50)
            completed_tasks = await self.get_tasks(completed=True, max_results=20)
            
            # Analyse des tâches
            pending_count = len(all_tasks)
            completed_count = len(completed_tasks)
            
            # Tâches avec échéance
            due_today = []
            due_soon = []
            overdue = []
            
            today = datetime.now().date()
            
            for task in all_tasks:
                if task['due']:
                    try:
                        due_date = datetime.fromisoformat(task['due'].replace('Z', '')).date()
                        if due_date == today:
                            due_today.append(task)
                        elif due_date < today:
                            overdue.append(task)
                        elif due_date <= today + timedelta(days=7):
                            due_soon.append(task)
                    except:
                        pass
            
            return {
                'total_pending': pending_count,
                'total_completed': completed_count,
                'due_today': len(due_today),
                'due_soon': len(due_soon),
                'overdue': len(overdue),
                'recent_tasks': all_tasks[:5],
                'productivity_score': min(100, (completed_count / max(1, completed_count + pending_count)) * 100)
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé tâches", error=str(e))
            return {
                'total_pending': 0,
                'total_completed': 0,
                'due_today': 0,
                'due_soon': 0,
                'overdue': 0,
                'recent_tasks': [],
                'productivity_score': 0
            }

# Instance globale du service
tasks_service = TasksService()
