#!/usr/bin/env python3
"""
🧪 Tests de validation KanterMator + Sylvie
Script pour vérifier que tous les composants fonctionnent
"""

import os
import sys
import asyncio
from typing import Dict, List
import structlog

# Configuration du logging pour les tests
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class KanterMatorValidator:
    """Validateur des composants KanterMator"""
    
    def __init__(self):
        self.results: Dict[str, bool] = {}
        
    async def run_all_tests(self) -> Dict[str, bool]:
        """Exécute tous les tests de validation"""
        logger.info("🧪 Début des tests de validation KanterMator + Sylvie")
        
        tests = [
            ("Configuration", self.test_configuration),
            ("Imports Python", self.test_imports),
            ("Base de données", self.test_database),
            ("Services Google", self.test_google_services),
            ("Agent Sylvie", self.test_sylvie),
            ("API Routes", self.test_api_routes),
            ("Scheduler", self.test_scheduler),
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Test: {test_name}")
                result = await test_func() if asyncio.iscoroutinefunction(test_func) else test_func()
                self.results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name}: OK")
                else:
                    logger.error(f"❌ {test_name}: ÉCHEC")
                    
            except Exception as e:
                logger.error(f"💥 {test_name}: ERREUR - {str(e)}")
                self.results[test_name] = False
        
        return self.results
    
    def test_configuration(self) -> bool:
        """Test de la configuration"""
        try:
            # Test d'import de la configuration
            from app.utils.config import settings
            
            # Vérifications de base
            checks = [
                settings.APP_NAME == "KanterMator",
                settings.VERSION == "1.0.0",
                bool(settings.DATABASE_URL),
                bool(settings.REDIS_URL),
            ]
            
            if all(checks):
                logger.info(f"Configuration chargée: {settings.ENVIRONMENT}")
                return True
            else:
                logger.warning("Certains paramètres de configuration sont manquants")
                return False
                
        except Exception as e:
            logger.error(f"Erreur configuration: {e}")
            return False
    
    def test_imports(self) -> bool:
        """Test des imports Python essentiels"""
        try:
            # Imports des modules principaux
            from app.services.google_auth import GoogleAuthService
            from app.services.drive_manager import DriveManager
            from app.services.sheets_reader import SheetsReader
            from app.services.scheduler import AutomationScheduler
            from app.services.sylvie_agent import SylvieAgent
            from app.utils.database import DatabaseManager
            from app.models import AutomationTask, Progression
            
            logger.info("Tous les modules Python importés avec succès")
            return True
            
        except ImportError as e:
            logger.error(f"Erreur d'import: {e}")
            return False
    
    def test_database(self) -> bool:
        """Test de la base de données"""
        try:
            from app.utils.database import db_manager
            
            # Test de santé de la base
            health = db_manager.health_check()
            
            if health:
                logger.info("Base de données accessible")
                return True
            else:
                logger.warning("Base de données non accessible (normal si pas démarrée)")
                return False
                
        except Exception as e:
            logger.error(f"Erreur base de données: {e}")
            return False
    
    def test_google_services(self) -> bool:
        """Test des services Google"""
        try:
            from app.services.google_auth import GoogleAuthService
            from app.services.drive_manager import DriveManager
            from app.services.sheets_reader import SheetsReader
            
            # Test d'initialisation (sans credentials réels)
            auth_service = GoogleAuthService()
            drive_manager = DriveManager()
            sheets_reader = SheetsReader()
            
            logger.info("Services Google initialisés (credentials non testés)")
            return True
            
        except Exception as e:
            logger.error(f"Erreur services Google: {e}")
            return False
    
    def test_sylvie(self) -> bool:
        """Test de l'agent Sylvie"""
        try:
            from app.services.sylvie_agent import SylvieAgent
            from app.services.sylvie_config import SylvieCapability
            from app.services.sylvie_monitoring import sylvie_monitor
            
            # Test d'initialisation
            agent = SylvieAgent()
            
            # Test des capacités
            capabilities = list(SylvieCapability)
            
            logger.info(f"Agent Sylvie initialisé avec {len(capabilities)} capacités")
            return True
            
        except Exception as e:
            logger.error(f"Erreur agent Sylvie: {e}")
            return False
    
    def test_api_routes(self) -> bool:
        """Test des routes API"""
        try:
            from app.routers import (
                progressions_router, 
                automation_router, 
                drive_router, 
                system_router
            )
            from app.routers_sylvie import sylvie_router
            
            # Comptage des routes
            routes_count = (
                len(progressions_router.routes) +
                len(automation_router.routes) +
                len(drive_router.routes) +
                len(system_router.routes) +
                len(sylvie_router.routes)
            )
            
            logger.info(f"Routes API chargées: {routes_count} endpoints")
            return True
            
        except Exception as e:
            logger.error(f"Erreur routes API: {e}")
            return False
    
    def test_scheduler(self) -> bool:
        """Test du planificateur"""
        try:
            from app.services.scheduler import AutomationScheduler, celery_app
            
            # Test d'initialisation
            scheduler = AutomationScheduler()
            
            # Test de la configuration Celery
            broker_url = celery_app.conf.broker_url
            
            logger.info(f"Scheduler et Celery configurés (broker: {broker_url})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur scheduler: {e}")
            return False
    
    def print_summary(self):
        """Affiche le résumé des tests"""
        logger.info("📊 Résumé des tests de validation")
        
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        for test_name, result in self.results.items():
            status = "✅" if result else "❌"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"🎯 Résultat: {passed}/{total} tests réussis")
        
        if passed == total:
            logger.info("🎉 Tous les tests sont passés ! KanterMator est prêt.")
        elif passed >= total * 0.8:
            logger.info("⚠️ La plupart des tests sont OK. Vérifiez les échecs mineurs.")
        else:
            logger.error("💥 Plusieurs tests ont échoué. Configuration requise.")

async def main():
    """Point d'entrée principal"""
    validator = KanterMatorValidator()
    
    try:
        results = await validator.run_all_tests()
        validator.print_summary()
        
        # Code de sortie basé sur les résultats
        success_rate = sum(1 for r in results.values() if r) / len(results)
        sys.exit(0 if success_rate >= 0.8 else 1)
        
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Erreur critique pendant les tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ajout du chemin Python
    sys.path.insert(0, "/Users/kanter/Desktop/mega-flemme")
    
    asyncio.run(main())
