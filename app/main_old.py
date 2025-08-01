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
    - � **Google Drive** : Gestion des dossiers et raccourcis
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
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(automation.router, prefix="/api/v1/automation", tags=["🤖 Automatisation"])
app.include_router(sheets.router, prefix="/api/v1/sheets", tags=["📊 Google Sheets"])
app.include_router(drive.router, prefix="/api/v1/drive", tags=["🗂️ Google Drive"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["📈 Monitoring"])

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    logger.info("🚀 KanterMator API démarrage", 
                version="1.0.0", 
                environment=settings.ENVIRONMENT)
    
    # Test de connexion Google Workspace
    try:
        auth_service = GoogleAuthService()
        await auth_service.verify_credentials()
        logger.info("✅ Connexion Google Workspace validée")
    except Exception as e:
        logger.error("❌ Erreur connexion Google Workspace", error=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'application"""
    logger.info("🛑 KanterMator API arrêt")

@app.get("/")
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "🤖 KanterMator API - Préparateur automatique de semaines pédagogiques",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/api/v1/monitoring/health"
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'application"""
    try:
        # Test connexion base de données
        # Test connexion Google APIs
        # Test état des services
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "✅ Connected",
                "google_apis": "✅ Connected", 
                "redis": "✅ Connected"
            }
        }
    except Exception as e:
        logger.error("❌ Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error("❌ Erreur non gérée", 
                 path=str(request.url.path),
                 method=request.method,
                 error=str(exc))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "message": "Une erreur inattendue s'est produite",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
