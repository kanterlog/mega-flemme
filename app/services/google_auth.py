"""
🔐 Google Authentication Service
Phase 2.2.1 - Module d'authentification OAuth

Gestion de l'authentification Google Workspace avec fallback
Inspiré des patterns goodls et google-workspace-samples
"""

import os
import json
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build
import structlog

logger = structlog.get_logger()

class GoogleAuthService:
    """Service d'authentification Google avec OAuth et Service Account"""
    
        # Scopes Google APIs étendus pour accès complet Google Workspace
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/contacts.readonly',
        'https://www.googleapis.com/auth/tasks',
        'https://www.googleapis.com/auth/tasks.readonly',
        'https://www.googleapis.com/auth/presentations',
        'https://www.googleapis.com/auth/documents'
    ]
    
    def __init__(self):
        self.credentials: Optional[Credentials] = None
        
        # Détection de l'environnement (Docker vs local)
        if os.path.exists("/app"):
            # Environnement Docker
            self.token_file = "/app/credentials/token.json"
            self.credentials_file = "/app/credentials/google-credentials.json" 
            self.service_account_file = "/app/credentials/service-account.json"
        else:
            # Environnement local de développement
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.token_file = os.path.join(base_path, "credentials", "token.json")
            self.credentials_file = os.path.join(base_path, "credentials", "google-credentials.json")
            self.service_account_file = os.path.join(base_path, "credentials", "service-account.json")
        
    async def get_credentials(self) -> Credentials:
        """
        Obtient les credentials Google avec fallback automatique
        
        Ordre de priorité :
        1. Token existant (OAuth)
        2. Service Account 
        3. Nouveau flow OAuth
        4. Escalade vers Sylvie
        """
        try:
            # 1. Essayer le token OAuth existant
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, self.SCOPES
                )
                
                # Renouveler si expiré
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_token()
                    logger.info("✅ Token OAuth renouvelé")
                    return self.credentials
                    
                if self.credentials and self.credentials.valid:
                    logger.info("✅ Token OAuth valide")
                    return self.credentials
            
            # 2. Service Account en fallback
            if os.path.exists(self.service_account_file):
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_file, scopes=self.SCOPES
                )
                logger.info("✅ Service Account utilisé")
                return self.credentials
            
            # 3. Nouveau flow OAuth interactif
            if os.path.exists(self.credentials_file):
                logger.warning("🔄 Nouvelle authentification OAuth requise")
                return await self._interactive_oauth_flow()
            
            # 4. Escalade vers Sylvie
            logger.error("❌ Aucun fichier de credentials trouvé")
            await self._escalate_to_sylvie("missing_credentials")
            raise Exception("Credentials Google non disponibles")
            
        except Exception as e:
            logger.error("❌ Erreur authentification Google", error=str(e))
            await self._escalate_to_sylvie("auth_error", str(e))
            raise
    
    async def _interactive_oauth_flow(self) -> Credentials:
        """Flow OAuth interactif pour obtenir des nouveaux tokens"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES
            )
            
            # Mode headless pour le serveur
            self.credentials = flow.run_local_server(
                port=8080,
                prompt='consent',
                authorization_prompt_message=""
            )
            
            self._save_token()
            logger.info("✅ Nouveau token OAuth obtenu")
            return self.credentials
            
        except Exception as e:
            logger.error("❌ Échec flow OAuth", error=str(e))
            raise
    
    def _save_token(self):
        """Sauvegarde du token OAuth"""
        try:
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            with open(self.token_file, 'w') as token:
                token.write(self.credentials.to_json())
            logger.info("💾 Token sauvegardé")
        except Exception as e:
            logger.error("❌ Erreur sauvegarde token", error=str(e))
    
    async def verify_credentials(self) -> bool:
        """Vérifie la validité des credentials"""
        try:
            credentials = await self.get_credentials()
            
            # Test avec l'API Drive
            service = build('drive', 'v3', credentials=credentials)
            service.about().get(fields="user").execute()
            
            logger.info("✅ Credentials Google validés")
            return True
            
        except Exception as e:
            logger.error("❌ Validation credentials échouée", error=str(e))
            return False
    
    async def get_service(self, service_name: str, version: str = 'v3'):
        """
        Obtient un service Google API
        
        Args:
            service_name: 'drive', 'sheets', 'calendar'
            version: Version de l'API
        """
        credentials = await self.get_credentials()
        
        # Mapping des versions par défaut
        versions = {
            'drive': 'v3',
            'sheets': 'v4', 
            'calendar': 'v3'
        }
        
        api_version = versions.get(service_name, version)
        service = build(service_name, api_version, credentials=credentials)
        
        logger.info(f"✅ Service {service_name} v{api_version} initialisé")
        return service
    
    async def _escalate_to_sylvie(self, error_type: str, details: str = ""):
        """
        Escalade vers Sylvie en cas de problème d'authentification
        
        Patterns d'erreur :
        - missing_credentials: Fichiers de credentials manquants
        - auth_error: Erreur d'authentification
        - token_expired: Token expiré sans refresh
        """
        escalation_data = {
            "type": "auth_error",
            "subtype": error_type,
            "timestamp": "2025-07-31T...",
            "details": details,
            "suggested_actions": {
                "missing_credentials": [
                    "Vérifier les fichiers de credentials",
                    "Reconfigurer OAuth si nécessaire"
                ],
                "auth_error": [
                    "Renouveler les tokens",
                    "Vérifier les permissions Google Cloud"
                ],
                "token_expired": [
                    "Processus de réautorisation requis"
                ]
            },
            "reauth_url": f"https://your-domain.com/auth/google/reauth"
        }
        
        # TODO: Intégration avec Sylvie API (Phase 3.3)
        logger.warning("🆘 Escalade vers Sylvie", escalation=escalation_data)
        
        # Simulation notification
        # await sylvie_api.notify_auth_issue(escalation_data)
    
    async def refresh_credentials(self) -> bool:
        """Force le renouvellement des credentials"""
        try:
            if self.credentials and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_token()
                logger.info("✅ Credentials renouvelés manuellement")
                return True
            else:
                logger.warning("⚠️ Impossible de renouveler - nouveau flow requis")
                return False
        except Exception as e:
            logger.error("❌ Erreur renouvellement", error=str(e))
            return False
