"""
🚀 Application principale KanterMator
Phase 2.6 - Application FastAPI complète

Agent d'automatisation Google Workspace pour l'éducation
Gestion intelligente des progressions pédagogiques
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

from app.utils.config import settings
from app.utils.database import init_database, db_manager
from app.routers import (
    progressions_router, 
    automation_router, 
    drive_router, 
    system_router
)

# Configuration structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Démarrage
    logger.info("🚀 Démarrage de KanterMator", 
               version=settings.VERSION,
               environment=settings.ENVIRONMENT)
    
    try:
        # Initialisation de la base de données
        init_database()
        logger.info("✅ Base de données initialisée")
        
        # Test de connexion aux services Google
        try:
            from app.services.google_auth import GoogleAuthService
            auth_service = GoogleAuthService()
            credentials = auth_service.get_credentials()
            logger.info("✅ Authentification Google validée")
        except Exception as e:
            logger.warning("⚠️ Problème d'authentification Google", error=str(e))
        
        # Test de connexion Redis (pour Celery)
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            logger.info("✅ Connexion Redis validée")
        except Exception as e:
            logger.warning("⚠️ Problème de connexion Redis", error=str(e))
            
    except Exception as e:
        logger.error("❌ Erreur lors de l'initialisation", error=str(e))
        raise
    
    yield
    
    # Arrêt
    logger.info("⏹️ Arrêt de KanterMator")

# Création de l'application FastAPI
app = FastAPI(
    title="KanterMator API",
    description="""
    🤖 **Agent d'automatisation Google Workspace pour l'éducation**
    
    KanterMator automatise la création de dossiers hebdomadaires, 
    la gestion des raccourcis et l'organisation pédagogique dans Google Drive
    à partir des progressions définies dans Google Sheets.
    
    ## Fonctionnalités
    
    - 📊 **Progressions** : Synchronisation depuis Google Sheets
    - 🤖 **Automatisation** : Planification et exécution des tâches
    - 📁 **Google Drive** : Gestion des dossiers et raccourcis
    - 🔧 **Système** : Monitoring et validation des intégrations
    
    ## Workflow
    
    1. Lecture des progressions hebdomadaires dans Google Sheets
    2. Automatisation programmée (samedi soir par défaut)
    3. Création de la structure de dossiers dans Google Drive
    4. Génération des raccourcis vers les ressources communes
    5. Archivage automatique des anciennes semaines
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(progressions_router, prefix="/api/v1")
app.include_router(automation_router, prefix="/api/v1")
app.include_router(drive_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# Gestionnaire d'exceptions global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global des exceptions"""
    logger.error("Exception non gérée", 
                path=request.url.path,
                method=request.method,
                error=str(exc),
                user_agent=request.headers.get("user-agent"))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "message": "Une erreur inattendue s'est produite",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "request_id": id(request)
        }
    )

# Routes de base
@app.get("/")
async def root():
    """Point d'entrée principal de l'API KanterMator"""
    return {
        "message": "🤖 KanterMator API - Agent d'automatisation éducative",
        "description": "Automatisation Google Workspace pour l'éducation",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "active",
        "automation_enabled": settings.AUTOMATION_ENABLED,
        "docs_url": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "progressions": "Gestion des progressions pédagogiques",
            "automation": "Automatisation hebdomadaire programmée",
            "drive_management": "Création de dossiers et raccourcis",
            "google_sheets": "Synchronisation avec Google Sheets",
            "monitoring": "Monitoring et validation système"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'application"""
    try:
        # Test de base de données
        db_healthy = db_manager.health_check()
        
        return {
            "status": "healthy" if db_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "kantermator-api",
            "version": settings.VERSION,
            "checks": {
                "database": "ok" if db_healthy else "error",
                "api": "ok"
            }
        }
    except Exception as e:
        logger.error("Erreur lors du health check", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "kantermator-api",
                "error": str(e)
            }
        )

@app.get("/info")
async def app_info():
    """Informations détaillées sur l'application"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "automation": {
            "enabled": settings.AUTOMATION_ENABLED,
            "schedule": settings.AUTOMATION_SCHEDULE,
            "timezone": settings.AUTOMATION_TIMEZONE
        },
        "google_workspace": {
            "sheets_configured": bool(settings.GOOGLE_SHEETS_ID),
            "drive_folders_configured": bool(settings.DRIVE_CAHIER_JOURNAL_ID and settings.DRIVE_ARCHIVE_ID)
        },
        "subjects": settings.SUBJECTS,
        "school_year": {
            "start": settings.SCHOOL_YEAR_START,
            "end": settings.SCHOOL_YEAR_END
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
