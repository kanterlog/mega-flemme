#!/usr/bin/env python3
"""
🧪 Test d'authentification Google OAuth
Phase 3.12 - Validation des credentials et connexion

Test de la configuration OAuth avant lancement complet
"""

import sys
import os
import asyncio

# Ajout du chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.google_auth import GoogleAuthService
import structlog

logger = structlog.get_logger(__name__)

async def test_google_auth():
    """Test de l'authentification Google"""
    
    print("🔐 Test d'authentification Google OAuth...")
    print("")
    
    try:
        # Initialisation du service d'authentification
        auth_service = GoogleAuthService()
        
        print(f"📁 Fichiers credentials recherchés :")
        print(f"├── Token: {auth_service.token_file}")
        print(f"├── Credentials: {auth_service.credentials_file}")
        print(f"└── Service Account: {auth_service.service_account_file}")
        print("")
        
        # Vérification de l'existence du fichier credentials
        if not os.path.exists(auth_service.credentials_file):
            print("❌ Fichier google-credentials.json non trouvé !")
            print(f"📍 Chemin attendu: {auth_service.credentials_file}")
            return False
        
        print("✅ Fichier credentials trouvé")
        
        # Test de récupération des credentials
        print("🔄 Tentative d'authentification...")
        credentials = await auth_service.get_credentials()
        
        if credentials:
            print("✅ Authentification réussie !")
            print(f"📊 Token valide: {credentials.valid}")
            print(f"🔄 Token expiré: {credentials.expired}")
            
            if credentials.expired:
                print("⚠️  Token expiré - renouvellement automatique")
            
            return True
        else:
            print("❌ Échec de l'authentification")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_google_auth())
    
    if success:
        print("")
        print("🎉 AUTHENTIFICATION GOOGLE CONFIGURÉE !")
        print("🚀 Vous pouvez maintenant lancer: docker-compose up")
    else:
        print("")
        print("❌ Configuration à vérifier")
        print("📋 Vérifiez que toutes les APIs sont activées dans Google Cloud Console")
