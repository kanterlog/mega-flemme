"""
🔍 Module de monitoring proactif de Sylvie
Phase 3.4 - Surveillance intelligente

Sylvie surveille le système et alerte automatiquement
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
from sqlalchemy.orm import Session

from app.utils.database import db_manager
from app.utils.config import settings
from app.models import AutomationTask, SystemLog
from app.services.google_auth import GoogleAuthService
from app.services.sheets_reader import SheetsReader
from app.services.drive_manager import DriveManager

logger = structlog.get_logger(__name__)

class SylvieMonitor:
    """Système de monitoring proactif de Sylvie"""
    
    def __init__(self):
        self.monitoring_active = False
        self.alerts_history: List[Dict[str, Any]] = []
        self.last_checks: Dict[str, datetime] = {}
        
    async def start_monitoring(self):
        """Démarrage du monitoring continu"""
        self.monitoring_active = True
        logger.info("🔍 Sylvie commence le monitoring proactif")
        
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(300)  # Vérification toutes les 5 minutes
            except Exception as e:
                logger.error("❌ Erreur dans le monitoring Sylvie", error=str(e))
                await asyncio.sleep(60)  # Attente réduite en cas d'erreur
    
    def stop_monitoring(self):
        """Arrêt du monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ Sylvie arrête le monitoring")
    
    async def _perform_health_checks(self):
        """Exécution des vérifications de santé"""
        checks = [
            ("database", self._check_database_health),
            ("google_auth", self._check_google_auth),
            ("automation_tasks", self._check_automation_tasks),
            ("system_resources", self._check_system_resources),
            ("error_patterns", self._check_error_patterns)
        ]
        
        for check_name, check_function in checks:
            try:
                await check_function()
                self.last_checks[check_name] = datetime.utcnow()
            except Exception as e:
                await self._create_alert(
                    severity="error",
                    component=check_name,
                    message=f"Échec de vérification {check_name}: {str(e)}",
                    auto_resolve=True
                )
    
    async def _check_database_health(self):
        """Vérification de la santé de la base de données"""
        try:
            # Test de connexion simple
            healthy = db_manager.health_check()
            
            if not healthy:
                await self._create_alert(
                    severity="critical",
                    component="database",
                    message="Base de données PostgreSQL inaccessible",
                    auto_resolve=True
                )
                return
            
            # Vérification des performances
            with db_manager.get_session() as session:
                start_time = datetime.utcnow()
                session.execute("SELECT COUNT(*) FROM automation_tasks")
                query_time = (datetime.utcnow() - start_time).total_seconds()
                
                if query_time > 5.0:  # Plus de 5 secondes
                    await self._create_alert(
                        severity="warning",
                        component="database",
                        message=f"Requête base de données lente: {query_time:.2f}s",
                        auto_resolve=False
                    )
                    
        except Exception as e:
            await self._create_alert(
                severity="critical",
                component="database",
                message=f"Erreur critique base de données: {str(e)}",
                auto_resolve=True
            )
    
    async def _check_google_auth(self):
        """Vérification de l'authentification Google"""
        try:
            auth_service = GoogleAuthService()
            
            # Test d'authentification
            credentials = auth_service.get_credentials()
            
            # Test d'accès Google Sheets
            sheets_reader = SheetsReader()
            validation = sheets_reader.validate_sheets_structure()
            
            if not validation.get("sheets_accessible", False):
                await self._create_alert(
                    severity="error",
                    component="google_sheets",
                    message="Google Sheets inaccessible - Vérification des permissions nécessaire",
                    auto_resolve=True
                )
            
            # Test d'accès Google Drive
            drive_manager = DriveManager()
            drive_validation = drive_manager.validate_drive_access()
            
            if not drive_validation.get("drive_accessible", False):
                await self._create_alert(
                    severity="error", 
                    component="google_drive",
                    message="Google Drive inaccessible - Vérification des permissions nécessaire",
                    auto_resolve=True
                )
                
        except Exception as e:
            await self._create_alert(
                severity="critical",
                component="google_auth",
                message=f"Échec authentification Google: {str(e)}",
                auto_resolve=True
            )
    
    async def _check_automation_tasks(self):
        """Surveillance des tâches d'automatisation"""
        try:
            with db_manager.get_session() as session:
                # Tâches bloquées (en cours depuis plus de 2h)
                stuck_threshold = datetime.utcnow() - timedelta(hours=2)
                stuck_tasks = session.query(AutomationTask).filter(
                    AutomationTask.status == 'running',
                    AutomationTask.started_at < stuck_threshold
                ).all()
                
                for task in stuck_tasks:
                    await self._create_alert(
                        severity="warning",
                        component="automation",
                        message=f"Tâche bloquée depuis 2h: {task.task_type} (ID: {task.id})",
                        auto_resolve=True,
                        metadata={"task_id": task.id, "task_type": task.task_type}
                    )
                
                # Tâches échouées récentes
                recent_threshold = datetime.utcnow() - timedelta(hours=24)
                failed_tasks = session.query(AutomationTask).filter(
                    AutomationTask.status == 'failed',
                    AutomationTask.created_at > recent_threshold
                ).count()
                
                if failed_tasks > 3:  # Plus de 3 échecs en 24h
                    await self._create_alert(
                        severity="warning",
                        component="automation",
                        message=f"{failed_tasks} tâches échouées dans les dernières 24h",
                        auto_resolve=False
                    )
                    
        except Exception as e:
            logger.error("❌ Erreur lors de la vérification des tâches", error=str(e))
    
    async def _check_system_resources(self):
        """Vérification des ressources système"""
        try:
            # Vérification de l'espace Google Drive
            drive_manager = DriveManager()
            storage_info = drive_manager.get_drive_space_info()
            
            if storage_info.get("usage_percentage", 0) > 85:
                await self._create_alert(
                    severity="warning",
                    component="google_drive",
                    message=f"Espace Google Drive bientôt plein: {storage_info.get('usage_percentage', 0):.1f}%",
                    auto_resolve=False
                )
            
            # Vérification de l'historique des conversations Sylvie
            # (À implémenter selon les besoins)
            
        except Exception as e:
            logger.warning("⚠️ Erreur lors de la vérification des ressources", error=str(e))
    
    async def _check_error_patterns(self):
        """Détection de patterns d'erreurs répétitives"""
        try:
            # Analyse des logs système récents
            recent_threshold = datetime.utcnow() - timedelta(hours=1)
            
            with db_manager.get_session() as session:
                error_logs = session.query(SystemLog).filter(
                    SystemLog.level == 'ERROR',
                    SystemLog.timestamp > recent_threshold
                ).all()
                
                # Groupement par composant
                error_counts = {}
                for log in error_logs:
                    component = log.component
                    error_counts[component] = error_counts.get(component, 0) + 1
                
                # Alerte si plus de 5 erreurs par composant en 1h
                for component, count in error_counts.items():
                    if count > 5:
                        await self._create_alert(
                            severity="warning",
                            component=component,
                            message=f"Erreurs répétitives détectées: {count} erreurs en 1h",
                            auto_resolve=True,
                            metadata={"error_count": count, "timeframe": "1h"}
                        )
                        
        except Exception as e:
            logger.warning("⚠️ Erreur lors de l'analyse des patterns", error=str(e))
    
    async def _create_alert(self, severity: str, component: str, message: str, 
                          auto_resolve: bool = False, metadata: Dict[str, Any] = None):
        """Création d'une alerte de monitoring"""
        
        alert = {
            "id": len(self.alerts_history) + 1,
            "severity": severity,
            "component": component, 
            "message": message,
            "timestamp": datetime.utcnow(),
            "auto_resolve": auto_resolve,
            "resolved": False,
            "metadata": metadata or {}
        }
        
        self.alerts_history.append(alert)
        
        # Log selon la sévérité
        if severity == "critical":
            logger.error("🚨 ALERTE CRITIQUE", **alert)
        elif severity == "error":
            logger.error("❌ ALERTE ERREUR", **alert)
        elif severity == "warning":
            logger.warning("⚠️ ALERTE AVERTISSEMENT", **alert)
        else:
            logger.info("ℹ️ ALERTE INFO", **alert)
        
        # Résolution automatique si activée
        if auto_resolve:
            await self._attempt_auto_resolution(alert)
    
    async def _attempt_auto_resolution(self, alert: Dict[str, Any]):
        """Tentative de résolution automatique d'une alerte"""
        
        component = alert["component"]
        
        try:
            if component == "google_auth":
                # Tentative de reconnexion Google
                auth_service = GoogleAuthService()
                credentials = auth_service.get_credentials()
                
                if credentials:
                    alert["resolved"] = True
                    alert["resolution"] = "Reconnexion Google réussie"
                    logger.info("✅ Résolution auto: Reconnexion Google")
            
            elif component == "database":
                # Test de reconnexion base de données
                if db_manager.health_check():
                    alert["resolved"] = True
                    alert["resolution"] = "Base de données accessible"
                    logger.info("✅ Résolution auto: Base de données OK")
            
            elif component == "automation":
                # Nettoyage des tâches bloquées
                task_id = alert.get("metadata", {}).get("task_id")
                if task_id:
                    with db_manager.get_session() as session:
                        task = session.query(AutomationTask).filter(AutomationTask.id == task_id).first()
                        if task and task.status == 'running':
                            task.status = 'failed'
                            task.error_message = "Tâche bloquée - arrêtée automatiquement par Sylvie"
                            task.completed_at = datetime.utcnow()
                            session.commit()
                            
                            alert["resolved"] = True
                            alert["resolution"] = f"Tâche {task_id} arrêtée automatiquement"
                            logger.info("✅ Résolution auto: Tâche bloquée arrêtée", task_id=task_id)
                            
        except Exception as e:
            logger.error("❌ Échec résolution automatique", alert_id=alert["id"], error=str(e))
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Récupération des alertes actives"""
        return [alert for alert in self.alerts_history if not alert.get("resolved", False)]
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Résumé des alertes"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "total_alerts": len(self.alerts_history),
            "active_alerts": len(active_alerts),
            "resolved_alerts": len(self.alerts_history) - len(active_alerts),
            "by_severity": {},
            "by_component": {},
            "last_check": max(self.last_checks.values()) if self.last_checks else None,
            "monitoring_active": self.monitoring_active
        }
        
        # Comptage par sévérité
        for alert in active_alerts:
            severity = alert["severity"]
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        # Comptage par composant
        for alert in active_alerts:
            component = alert["component"]
            summary["by_component"][component] = summary["by_component"].get(component, 0) + 1
        
        return summary
    
    def clear_resolved_alerts(self):
        """Nettoyage des alertes résolues anciennes"""
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        self.alerts_history = [
            alert for alert in self.alerts_history
            if not alert.get("resolved", False) or alert["timestamp"] > cutoff_date
        ]
        
        logger.info("🧹 Nettoyage des alertes résolues anciennes")

# Instance globale du monitoring Sylvie
sylvie_monitor = SylvieMonitor()
