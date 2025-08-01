"""
🌐 Routeurs API KanterMator
Phase 2.6 - Endpoints REST

Définition des routes FastAPI pour l'interface
avec le système KanterMator
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
import structlog

from app.utils.database import get_database_session
from app.models import (
    ProgressionResponse, AutomationTaskResponse, DriveFolderResponse,
    DriveShortcutResponse, WeeklyAutomationRequest, WeeklyAutomationResponse,
    SystemStatusResponse
)
from app.services.sheets_reader import SheetsReader
from app.services.drive_manager import DriveManager
from app.services.scheduler import AutomationScheduler
from app.utils.config import settings

logger = structlog.get_logger(__name__)

# 📊 Router Progressions
progressions_router = APIRouter(prefix="/progressions", tags=["Progressions"])

@progressions_router.get("/", response_model=List[ProgressionResponse])
async def get_progressions(
    week_number: Optional[int] = Query(None, ge=1, le=53),
    year: Optional[int] = Query(None, ge=2020, le=2030),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_database_session)
):
    """
    Récupération des progressions pédagogiques
    
    Filtres disponibles:
    - week_number: Numéro de semaine
    - year: Année
    - subject: Matière
    """
    try:
        from app.models import Progression
        
        query = db.query(Progression)
        
        if week_number:
            query = query.filter(Progression.week_number == week_number)
        if year:
            query = query.filter(Progression.year == year)
        if subject:
            query = query.filter(Progression.subject == subject)
            
        progressions = query.order_by(Progression.week_number, Progression.subject).all()
        
        logger.info("Progressions récupérées", 
                   count=len(progressions),
                   filters={'week': week_number, 'year': year, 'subject': subject})
        
        return progressions
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des progressions", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des progressions")

@progressions_router.get("/week/{week_number}/{year}", response_model=List[ProgressionResponse])
async def get_week_progressions(
    week_number: int,
    year: int,
    db: Session = Depends(get_database_session)
):
    """Récupération des progressions pour une semaine spécifique"""
    try:
        from app.models import Progression
        
        progressions = db.query(Progression).filter(
            Progression.week_number == week_number,
            Progression.year == year
        ).all()
        
        if not progressions:
            raise HTTPException(status_code=404, detail="Aucune progression trouvée pour cette semaine")
        
        return progressions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erreur lors de la récupération des progressions de la semaine", 
                    week=week_number, year=year, error=str(e))
        raise HTTPException(status_code=500, detail="Erreur serveur")

@progressions_router.post("/sync")
async def sync_progressions_from_sheets(
    background_tasks: BackgroundTasks,
    force: bool = Query(False, description="Forcer la synchronisation même si récente"),
    db: Session = Depends(get_database_session)
):
    """
    Synchronisation des progressions depuis Google Sheets
    """
    try:
        sheets_reader = SheetsReader()
        
        # Lecture depuis Google Sheets
        progressions_data = sheets_reader.read_progressions_sheet()
        
        if not progressions_data:
            raise HTTPException(status_code=404, detail="Aucune progression trouvée dans Google Sheets")
        
        # Insertion/mise à jour en base
        from app.models import Progression
        
        synced_count = 0
        updated_count = 0
        
        for prog_data in progressions_data:
            # Recherche si la progression existe déjà
            existing = db.query(Progression).filter(
                Progression.week_number == prog_data['week_number'],
                Progression.year == prog_data['year'],
                Progression.subject == prog_data['subject']
            ).first()
            
            if existing:
                # Mise à jour
                for key, value in prog_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Création
                progression = Progression(**prog_data)
                db.add(progression)
                synced_count += 1
        
        db.commit()
        
        logger.info("Synchronisation terminée", 
                   synced=synced_count, 
                   updated=updated_count)
        
        return {
            "status": "success",
            "synced": synced_count,
            "updated": updated_count,
            "total": len(progressions_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erreur lors de la synchronisation", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la synchronisation")

# 🤖 Router Automatisation
automation_router = APIRouter(prefix="/automation", tags=["Automatisation"])

@automation_router.post("/schedule", response_model=WeeklyAutomationResponse)
async def schedule_weekly_automation(
    request: WeeklyAutomationRequest,
    background_tasks: BackgroundTasks
):
    """
    Planification de l'automatisation hebdomadaire
    """
    try:
        scheduler = AutomationScheduler()
        
        result = scheduler.schedule_weekly_automation(
            week_number=request.week_number,
            year=request.year,
            force=request.force_recreate
        )
        
        if result['status'] == 'scheduled':
            return WeeklyAutomationResponse(
                week_number=result['week_number'],
                year=result['year'],
                status="scheduled",
                folders_created=0,
                shortcuts_created=0,
                errors=[],
                execution_time=0.0
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('message', 'Erreur de planification'))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erreur lors de la planification", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la planification")

@automation_router.post("/execute", response_model=WeeklyAutomationResponse)
async def execute_weekly_automation(
    request: WeeklyAutomationRequest,
    background_tasks: BackgroundTasks
):
    """
    Exécution immédiate de l'automatisation hebdomadaire
    """
    try:
        start_time = datetime.now()
        
        # Lecture des progressions
        sheets_reader = SheetsReader()
        progressions = sheets_reader.get_week_progressions(request.week_number, request.year)
        
        if not progressions:
            raise HTTPException(status_code=404, detail="Aucune progression trouvée pour cette semaine")
        
        # Création de la structure Drive
        drive_manager = DriveManager()
        result = drive_manager.create_weekly_folder_structure(
            week_number=request.week_number,
            year=request.year,
            progressions=progressions
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return WeeklyAutomationResponse(
            week_number=request.week_number,
            year=request.year,
            status="completed",
            folders_created=len(result.get('subject_folders', {})) + (1 if result.get('week_folder_id') else 0),
            shortcuts_created=len(result.get('shortcuts_created', [])),
            errors=result.get('errors', []),
            execution_time=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erreur lors de l'exécution", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de l'exécution")

@automation_router.get("/tasks", response_model=List[AutomationTaskResponse])
async def get_automation_tasks(
    status: Optional[str] = Query(None),
    week_number: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_database_session)
):
    """Récupération des tâches d'automatisation"""
    try:
        from app.models import AutomationTask
        
        query = db.query(AutomationTask)
        
        if status:
            query = query.filter(AutomationTask.status == status)
        if week_number:
            query = query.filter(AutomationTask.week_number == week_number)
        if year:
            query = query.filter(AutomationTask.year == year)
            
        tasks = query.order_by(AutomationTask.created_at.desc()).limit(limit).all()
        
        return tasks
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des tâches", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur serveur")

# 📁 Router Google Drive
drive_router = APIRouter(prefix="/drive", tags=["Google Drive"])

@drive_router.get("/folders", response_model=List[DriveFolderResponse])
async def get_drive_folders(
    week_number: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_database_session)
):
    """Récupération des dossiers Drive gérés"""
    try:
        from app.models import DriveFolder
        
        query = db.query(DriveFolder)
        
        if week_number:
            query = query.filter(DriveFolder.week_number == week_number)
        if year:
            query = query.filter(DriveFolder.year == year)
        if subject:
            query = query.filter(DriveFolder.subject == subject)
            
        folders = query.order_by(DriveFolder.created_at.desc()).all()
        
        return folders
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des dossiers", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur serveur")

@drive_router.get("/shortcuts", response_model=List[DriveShortcutResponse])
async def get_drive_shortcuts(
    week_number: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_database_session)
):
    """Récupération des raccourcis Drive gérés"""
    try:
        from app.models import DriveShortcut
        
        query = db.query(DriveShortcut)
        
        if week_number:
            query = query.filter(DriveShortcut.week_number == week_number)
        if year:
            query = query.filter(DriveShortcut.year == year)
        if subject:
            query = query.filter(DriveShortcut.subject == subject)
            
        shortcuts = query.order_by(DriveShortcut.created_at.desc()).all()
        
        return shortcuts
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des raccourcis", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur serveur")

@drive_router.post("/archive")
async def archive_old_folders(
    weeks_to_keep: int = Query(4, ge=1, le=20),
    background_tasks: BackgroundTasks
):
    """Archivage des anciens dossiers"""
    try:
        drive_manager = DriveManager()
        result = drive_manager.archive_old_weeks(weeks_to_keep)
        
        return {
            "status": "completed",
            "folders_archived": result.get("folders_archived", 0),
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        logger.error("Erreur lors de l'archivage", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de l'archivage")

@drive_router.get("/storage")
async def get_drive_storage_info():
    """Informations sur l'espace de stockage Google Drive"""
    try:
        drive_manager = DriveManager()
        storage_info = drive_manager.get_drive_space_info()
        
        return storage_info
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des infos de stockage", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur serveur")

# 🔧 Router Système
system_router = APIRouter(prefix="/system", tags=["Système"])

@system_router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(db: Session = Depends(get_database_session)):
    """État général du système KanterMator"""
    try:
        from app.models import AutomationTask
        from app.utils.database import db_manager
        
        # Vérification de la base de données
        db_status = "ok" if db_manager.health_check() else "error"
        
        # Vérification de l'authentification Google
        try:
            sheets_reader = SheetsReader()
            sheets_validation = sheets_reader.validate_sheets_structure()
            google_auth_status = "ok" if sheets_validation['sheets_accessible'] else "error"
        except:
            google_auth_status = "error"
        
        # Tâches en attente
        pending_tasks = db.query(AutomationTask).filter(
            AutomationTask.status == 'pending'
        ).count()
        
        # Dernière automatisation
        last_automation = db.query(AutomationTask).filter(
            AutomationTask.status == 'completed'
        ).order_by(AutomationTask.completed_at.desc()).first()
        
        return SystemStatusResponse(
            status="ok" if db_status == "ok" and google_auth_status == "ok" else "warning",
            version=settings.VERSION,
            automation_enabled=settings.AUTOMATION_ENABLED,
            last_automation=last_automation.completed_at if last_automation else None,
            pending_tasks=pending_tasks,
            database_status=db_status,
            google_auth_status=google_auth_status
        )
        
    except Exception as e:
        logger.error("Erreur lors de la récupération du statut système", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur serveur")

@system_router.get("/health")
async def health_check():
    """Health check simple pour monitoring"""
    try:
        from app.utils.database import db_manager
        
        db_ok = db_manager.health_check()
        
        if db_ok:
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        else:
            raise HTTPException(status_code=503, detail="Base de données inaccessible")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erreur lors du health check", error=str(e))
        raise HTTPException(status_code=503, detail="Erreur système")

@system_router.post("/validate")
async def validate_integrations():
    """Validation de toutes les intégrations"""
    try:
        results = {}
        
        # Validation Google Sheets
        try:
            sheets_reader = SheetsReader()
            results['google_sheets'] = sheets_reader.validate_sheets_structure()
        except Exception as e:
            results['google_sheets'] = {'error': str(e)}
        
        # Validation Google Drive
        try:
            drive_manager = DriveManager()
            results['google_drive'] = drive_manager.validate_drive_access()
        except Exception as e:
            results['google_drive'] = {'error': str(e)}
        
        # Validation base de données
        from app.utils.database import db_manager
        results['database'] = {'accessible': db_manager.health_check()}
        
        return results
        
    except Exception as e:
        logger.error("Erreur lors de la validation", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la validation")

# Import des routeurs Sylvie
from app.routers_sylvie import sylvie_router
