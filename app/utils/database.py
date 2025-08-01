"""
🗄️ Gestionnaire de base de données KanterMator
Phase 2.2 - Configuration SQLAlchemy

Configuration et gestion de la base de données PostgreSQL
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import structlog
from app.utils.config import settings
from app.models import Base

logger = structlog.get_logger(__name__)

class DatabaseManager:
    """Gestionnaire centralisé de la base de données"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Initialisation de la connexion à la base de données"""
        try:
            # Configuration de l'engine SQLAlchemy
            self.engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,  # Vérification de la connexion
                pool_recycle=3600,   # Recyclage des connexions après 1h
                echo=settings.LOG_LEVEL == "DEBUG"  # Logs SQL en mode debug
            )
            
            # Configuration du sessionmaker
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Événement de logging pour les connexions
            @event.listens_for(self.engine, "connect")
            def receive_connect(dbapi_connection, connection_record):
                logger.info("Nouvelle connexion à la base de données établie")
            
            @event.listens_for(self.engine, "checkout")
            def receive_checkout(dbapi_connection, connection_record, connection_proxy):
                logger.debug("Connexion extraite du pool")
            
            logger.info("Gestionnaire de base de données initialisé", 
                       database_url=settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL)
            
        except Exception as e:
            logger.error("Erreur lors de l'initialisation de la base de données", error=str(e))
            raise
    
    def create_tables(self):
        """Création de toutes les tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tables de base de données créées avec succès")
        except Exception as e:
            logger.error("Erreur lors de la création des tables", error=str(e))
            raise
    
    def drop_tables(self):
        """Suppression de toutes les tables (ATTENTION!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("Toutes les tables ont été supprimées")
        except Exception as e:
            logger.error("Erreur lors de la suppression des tables", error=str(e))
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager pour les sessions de base de données"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Erreur dans la session de base de données", error=str(e))
            raise
        finally:
            session.close()
    
    def get_db_session(self) -> Session:
        """Générateur de session pour FastAPI Depends"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Vérification de l'état de la base de données"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error("Échec du health check de la base de données", error=str(e))
            return False

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

# Fonction d'aide pour FastAPI
def get_database_session():
    """Dépendance FastAPI pour obtenir une session de base de données"""
    return db_manager.get_db_session()

# Fonctions utilitaires pour les migrations et la maintenance

def init_database():
    """Initialisation complète de la base de données"""
    logger.info("Initialisation de la base de données...")
    db_manager.create_tables()
    logger.info("Base de données initialisée avec succès")

def reset_database():
    """Réinitialisation complète de la base de données (DANGER!)"""
    logger.warning("Réinitialisation de la base de données...")
    db_manager.drop_tables()
    db_manager.create_tables()
    logger.info("Base de données réinitialisée")
