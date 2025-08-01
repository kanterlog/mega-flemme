#!/usr/bin/env python3
"""
🚀 Serveur simple pour Sylvie
Interface web pour KanterMator avec Sylvie Agent
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.routers.sylvie_router import sylvie_router

# Configuration du logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Création de l'application FastAPI
app = FastAPI(
    title="🤖 Sylvie - Assistant KanterMator",
    description="Interface conversationnelle avec IA hybride et Google Workspace",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Ajout du router Sylvie
app.include_router(sylvie_router)

@app.get("/")
async def redirect_to_sylvie():
    """Redirection vers l'interface Sylvie"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/sylvie/")

@app.get("/health")
async def health_check():
    """Point de contrôle de santé"""
    return {
        "status": "ok",
        "service": "Sylvie Assistant",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
