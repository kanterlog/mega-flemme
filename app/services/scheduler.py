"""
⏰ Service Scheduler pour Sylvie
Phase 3.12 - Planificateur d'automatisations

Gestion des tâches automatisées et de la planification pour KanterMator
"""

import structlog
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class ScheduledTask:
    """Représente une tâche planifiée"""
    id: str
    name: str
    function: Callable
    args: List[Any]
    kwargs: Dict[str, Any]
    scheduled_time: datetime
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class AutomationScheduler:
    """Service de planification et d'exécution de tâches automatisées"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.task_queue = []
        self._scheduler_task = None
        
        logger.info("⏰ Scheduler d'automatisation initialisé")
    
    async def start(self):
        """Démarre le scheduler"""
        if self.running:
            logger.warning("⚠️ Scheduler déjà en cours")
            return
        
        self.running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("✅ Scheduler démarré")
    
    async def stop(self):
        """Arrête le scheduler"""
        self.running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Scheduler arrêté")
    
    async def schedule_task(
        self,
        name: str,
        function: Callable,
        scheduled_time: datetime,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3
    ) -> str:
        """
        Planifie une nouvelle tâche
        
        Args:
            name: Nom de la tâche
            function: Fonction à exécuter
            scheduled_time: Moment d'exécution planifié
            args: Arguments positionnels
            kwargs: Arguments nommés
            priority: Priorité de la tâche
            max_retries: Nombre maximum de tentatives
            
        Returns:
            ID de la tâche planifiée
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.tasks)}"
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            function=function,
            args=args or [],
            kwargs=kwargs or {},
            scheduled_time=scheduled_time,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        logger.info("📅 Tâche planifiée", task_id=task_id, name=name, scheduled_time=scheduled_time)
        
        return task_id
    
    async def schedule_recurring_task(
        self,
        name: str,
        function: Callable,
        interval_minutes: int,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> List[str]:
        """
        Planifie une tâche récurrente
        
        Args:
            name: Nom de la tâche
            function: Fonction à exécuter
            interval_minutes: Intervalle en minutes
            args: Arguments positionnels
            kwargs: Arguments nommés
            priority: Priorité de la tâche
            
        Returns:
            Liste des IDs des tâches planifiées
        """
        task_ids = []
        now = datetime.now()
        
        # Planifie les 24 prochaines heures
        for i in range(0, 24 * 60, interval_minutes):
            scheduled_time = now + timedelta(minutes=i)
            
            task_id = await self.schedule_task(
                name=f"{name}_recurring_{i//interval_minutes}",
                function=function,
                scheduled_time=scheduled_time,
                args=args,
                kwargs=kwargs,
                priority=priority
            )
            task_ids.append(task_id)
        
        logger.info("🔄 Tâche récurrente planifiée", name=name, interval=interval_minutes, count=len(task_ids))
        return task_ids
    
    async def cancel_task(self, task_id: str) -> bool:
        """Annule une tâche planifiée"""
        if task_id not in self.tasks:
            logger.warning("⚠️ Tâche introuvable", task_id=task_id)
            return False
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.RUNNING:
            logger.warning("⚠️ Impossible d'annuler une tâche en cours", task_id=task_id)
            return False
        
        task.status = TaskStatus.CANCELLED
        logger.info("❌ Tâche annulée", task_id=task_id)
        return True
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une tâche"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'id': task.id,
            'name': task.name,
            'status': task.status.value,
            'priority': task.priority.value,
            'scheduled_time': task.scheduled_time.isoformat(),
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message,
            'retry_count': task.retry_count
        }
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Récupère toutes les tâches en attente"""
        pending_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                pending_tasks.append({
                    'id': task.id,
                    'name': task.name,
                    'scheduled_time': task.scheduled_time.isoformat(),
                    'priority': task.priority.value
                })
        
        # Tri par priorité puis par heure
        pending_tasks.sort(key=lambda x: (x['priority'], x['scheduled_time']), reverse=True)
        return pending_tasks
    
    async def _scheduler_loop(self):
        """Boucle principale du scheduler"""
        while self.running:
            try:
                await self._process_pending_tasks()
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Erreur dans la boucle du scheduler", error=str(e))
                await asyncio.sleep(60)  # Attente plus longue en cas d'erreur
    
    async def _process_pending_tasks(self):
        """Traite les tâches en attente"""
        now = datetime.now()
        tasks_to_execute = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                task.scheduled_time <= now):
                tasks_to_execute.append(task)
        
        # Tri par priorité
        tasks_to_execute.sort(key=lambda x: x.priority.value, reverse=True)
        
        for task in tasks_to_execute:
            await self._execute_task(task)
    
    async def _execute_task(self, task: ScheduledTask):
        """Exécute une tâche"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            logger.info("🚀 Exécution de la tâche", task_id=task.id, name=task.name)
            
            # Exécution de la fonction
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args, **task.kwargs)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info("✅ Tâche terminée avec succès", task_id=task.id, name=task.name)
            
        except Exception as e:
            task.retry_count += 1
            error_msg = str(e)
            
            if task.retry_count <= task.max_retries:
                task.status = TaskStatus.PENDING
                # Nouvelle tentative dans 5 minutes
                task.scheduled_time = datetime.now() + timedelta(minutes=5)
                
                logger.warning("⚠️ Erreur tâche, nouvelle tentative programmée", 
                             task_id=task.id, error=error_msg, retry=task.retry_count)
            else:
                task.status = TaskStatus.FAILED
                task.error_message = error_msg
                task.completed_at = datetime.now()
                
                logger.error("❌ Tâche échouée définitivement", 
                           task_id=task.id, error=error_msg, retries=task.retry_count)
    
    async def get_scheduler_summary_for_sylvie(self) -> Dict[str, Any]:
        """Génère un résumé du scheduler pour Sylvie"""
        try:
            pending_count = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
            running_count = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING])
            completed_count = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
            failed_count = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
            
            # Prochaines tâches
            next_tasks = []
            now = datetime.now()
            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING and task.scheduled_time > now:
                    next_tasks.append({
                        'name': task.name,
                        'scheduled_time': task.scheduled_time.isoformat(),
                        'priority': task.priority.value
                    })
            
            next_tasks.sort(key=lambda x: x['scheduled_time'])
            next_tasks = next_tasks[:5]  # Top 5
            
            return {
                'scheduler_running': self.running,
                'total_tasks': len(self.tasks),
                'pending_tasks': pending_count,
                'running_tasks': running_count,
                'completed_tasks': completed_count,
                'failed_tasks': failed_count,
                'next_tasks': next_tasks,
                'health_status': 'healthy' if failed_count < 5 else 'degraded'
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé scheduler", error=str(e))
            return {
                'scheduler_running': self.running,
                'total_tasks': 0,
                'pending_tasks': 0,
                'running_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'next_tasks': [],
                'health_status': 'unknown'
            }

# Instance globale du scheduler
automation_scheduler = AutomationScheduler()

