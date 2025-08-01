"""
🚀 Application principale KanterMator + Sylvie
Phase 3.5 - Application complète avec agent Sylvie

Agent d'automatisation Google Workspace + Interface conversationnelle
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from datetime import datetime
import asyncio

from app.utils.config import settings
from app.utils.database import init_database, db_manager
from app.routers import (
    progressions_router, 
    automation_router, 
    drive_router, 
    system_router
)
from app.routers_sylvie import sylvie_router
from app.services.sylvie_monitoring import sylvie_monitor

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
    """Gestionnaire de cycle de vie de l'application avec Sylvie"""
    # Démarrage
    logger.info("🚀 Démarrage de KanterMator + Sylvie", 
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
        
        # Démarrage du monitoring Sylvie
        try:
            monitoring_task = asyncio.create_task(sylvie_monitor.start_monitoring())
            logger.info("🔍 Monitoring Sylvie démarré")
        except Exception as e:
            logger.warning("⚠️ Problème démarrage monitoring Sylvie", error=str(e))
            
    except Exception as e:
        logger.error("❌ Erreur lors de l'initialisation", error=str(e))
        raise
    
    yield
    
    # Arrêt
    logger.info("⏹️ Arrêt de KanterMator + Sylvie")
    sylvie_monitor.stop_monitoring()

# Création de l'application FastAPI
app = FastAPI(
    title="KanterMator + Sylvie API",
    description="""
    🤖 **Agent d'automatisation Google Workspace + Assistant IA conversationnel**
    
    ## KanterMator
    Automatise la création de dossiers hebdomadaires, la gestion des raccourcis 
    et l'organisation pédagogique dans Google Drive à partir des progressions 
    définies dans Google Sheets.
    
    ## Sylvie
    Votre assistante IA conversationnelle qui contrôle KanterMator en langage naturel,
    surveille le système et résout automatiquement les problèmes.
    
    ## Fonctionnalités
    
    ### 📊 KanterMator Backend
    - **Progressions** : Synchronisation depuis Google Sheets
    - **Automatisation** : Planification et exécution des tâches
    - **Google Drive** : Gestion des dossiers et raccourcis
    - **Système** : Monitoring et validation des intégrations
    
    ### 🤖 Sylvie Agent IA
    - **Conversation naturelle** : Contrôlez tout en parlant normalement
    - **Monitoring proactif** : Surveillance automatique 24/7
    - **Résolution d'incidents** : Correction automatique des problèmes
    - **Aide contextuelle** : Guidance intelligente et suggestions
    
    ## Workflow Complet
    
    1. **Parlez à Sylvie** : "Lance l'automatisation pour cette semaine"
    2. **Sylvie analyse** votre demande et vos progressions Google Sheets
    3. **KanterMator exécute** automatiquement la création des dossiers
    4. **Sylvie vous informe** du résultat et propose la suite
    5. **Monitoring continu** : Sylvie surveille et alerte en cas de problème
    
    ## Commandes Sylvie
    
    Parlez naturellement à Sylvie :
    - "Lance l'automatisation pour la semaine 32"
    - "Vérifie mes progressions Google Sheets"
    - "Comment va le système ?"
    - "Archive les dossiers de plus de 4 semaines"
    - "Aide-moi à configurer KanterMator"
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
app.include_router(sylvie_router, prefix="/api/v1")  # 🤖 Sylvie

# Gestionnaire d'exceptions global avec notification Sylvie
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global des exceptions avec alerte Sylvie"""
    
    # Log de l'erreur
    logger.error("Exception non gérée", 
                path=request.url.path,
                method=request.method,
                error=str(exc),
                user_agent=request.headers.get("user-agent"))
    
    # Notification à Sylvie pour monitoring
    try:
        await sylvie_monitor._create_alert(
            severity="error",
            component="api",
            message=f"Exception non gérée sur {request.url.path}: {str(exc)}",
            auto_resolve=False,
            metadata={
                "path": request.url.path,
                "method": request.method,
                "error": str(exc)
            }
        )
    except:
        pass  # Ne pas faire échouer la réponse si Sylvie a un problème
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "message": "Une erreur inattendue s'est produite. Sylvie a été notifiée.",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "request_id": id(request),
            "sylvie_notified": True
        }
    )

# Routes de base
@app.get("/")
async def root():
    """Point d'entrée principal de l'API KanterMator + Sylvie"""
    
    # Récupération du statut de monitoring Sylvie
    monitoring_summary = sylvie_monitor.get_alerts_summary()
    
    return {
        "message": "🤖 KanterMator + Sylvie - Agent d'automatisation éducative avec IA",
        "description": "Automatisation Google Workspace + Assistant conversationnel",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "active",
        "automation_enabled": settings.AUTOMATION_ENABLED,
        "docs_url": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "kantermator": {
                "description": "Backend d'automatisation Google Workspace",
                "features": [
                    "Gestion des progressions pédagogiques",
                    "Automatisation hebdomadaire programmée", 
                    "Création de dossiers et raccourcis",
                    "Synchronisation Google Sheets",
                    "Monitoring et validation système"
                ]
            },
            "sylvie": {
                "description": "Assistant IA conversationnel",
                "features": [
                    "Contrôle en langage naturel",
                    "Monitoring proactif 24/7",
                    "Résolution automatique d'incidents",
                    "Aide contextuelle intelligente",
                    "Suggestions personnalisées"
                ],
                "monitoring": {
                    "active": monitoring_summary["monitoring_active"],
                    "active_alerts": monitoring_summary["active_alerts"],
                    "last_check": monitoring_summary["last_check"].isoformat() if monitoring_summary["last_check"] else None
                }
            }
        },
        "quick_start": {
            "chat_with_sylvie": "/api/v1/sylvie/chat",
            "sylvie_capabilities": "/api/v1/sylvie/capabilities",
            "system_status": "/api/v1/system/status",
            "demo_messages": "/api/v1/sylvie/demo-messages"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé complète (KanterMator + Sylvie)"""
    try:
        # Test de base de données
        db_healthy = db_manager.health_check()
        
        # Statut de Sylvie
        sylvie_status = sylvie_monitor.get_alerts_summary()
        sylvie_healthy = sylvie_status["active_alerts"] == 0
        
        overall_status = "healthy" if db_healthy and sylvie_healthy else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "kantermator-sylvie-api",
            "version": settings.VERSION,
            "checks": {
                "database": "ok" if db_healthy else "error",
                "api": "ok",
                "sylvie_monitoring": "ok" if sylvie_healthy else "warning",
                "sylvie_alerts": sylvie_status["active_alerts"]
            },
            "sylvie": {
                "monitoring_active": sylvie_status["monitoring_active"],
                "total_alerts": sylvie_status["total_alerts"],
                "active_alerts": sylvie_status["active_alerts"],
                "last_check": sylvie_status["last_check"].isoformat() if sylvie_status["last_check"] else None
            }
        }
    except Exception as e:
        logger.error("Erreur lors du health check", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "kantermator-sylvie-api",
                "error": str(e)
            }
        )

@app.get("/info")
async def app_info():
    """Informations détaillées sur l'application complète"""
    
    # Récupération des alertes Sylvie
    monitoring_summary = sylvie_monitor.get_alerts_summary()
    active_alerts = sylvie_monitor.get_active_alerts()
    
    return {
        "application": {
            "name": f"{settings.APP_NAME} + Sylvie",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        },
        "kantermator": {
            "automation": {
                "enabled": settings.AUTOMATION_ENABLED,
                "schedule": settings.AUTOMATION_SCHEDULE,
                "timezone": settings.AUTOMATION_TIMEZONE
            },
            "google_workspace": {
                "sheets_configured": bool(settings.GOOGLE_SHEETS_ID),
                "drive_folders_configured": bool(settings.DRIVE_CAHIER_JOURNAL_ID and settings.DRIVE_ARCHIVE_ID)
            },
            "education": {
                "subjects": settings.SUBJECTS,
                "school_year": {
                    "start": settings.SCHOOL_YEAR_START,
                    "end": settings.SCHOOL_YEAR_END
                }
            }
        },
        "sylvie": {
            "model": settings.OPENAI_MODEL,
            "monitoring": monitoring_summary,
            "capabilities": [
                "Contrôle d'automatisation",
                "Analyse des progressions", 
                "Gestion Google Drive",
                "Monitoring système",
                "Aide et guidance",
                "Résolution d'erreurs"
            ],
            "active_alerts": active_alerts[:5] if active_alerts else []  # 5 premières alertes
        }
    }

# Route spéciale pour tester Sylvie rapidement
@app.get("/sylvie-demo")
async def sylvie_demo():
    """Page de démonstration rapide de Sylvie"""
    return {
        "title": "🤖 Démonstration Sylvie",
        "description": "Testez votre assistante IA conversationnelle",
        "quick_test": {
            "endpoint": "/api/v1/sylvie/chat",
            "method": "POST",
            "body_example": {
                "message": "Bonjour Sylvie ! Comment va le système ?"
            }
        },
        "demo_messages": [
            "Bonjour Sylvie !",
            "Vérifie l'état du système",
            "Lance l'automatisation pour cette semaine",
            "Analyse mes progressions Google Sheets",
            "Que peux-tu faire pour moi ?",
            "Y a-t-il des problèmes à résoudre ?"
        ],
        "monitoring_status": sylvie_monitor.get_alerts_summary()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_sylvie:app", 
        host="0.0.0.0", 
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
