#!/usr/bin/env python3
"""
🔐 Script d'initialisation de l'authentification Google
Génère le token d'accès pour Sylvie
"""

import asyncio
import os
import sys

# Ajout du chemin parent pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.google_auth import GoogleAuthService

async def init_google_auth():
    """Initialise l'authentification Google pour Sylvie"""
    print("🔐 Initialisation de l'authentification Google pour Sylvie...")
    
    auth_service = GoogleAuthService()
    
    try:
        credentials = await auth_service.get_credentials()
        if credentials:
            print("✅ Authentification Google réussie !")
            print("🤖 Sylvie a maintenant accès à :")
            print("  📧 Gmail (lecture/envoi)")
            print("  📅 Google Calendar")
            print("  📁 Google Drive")
            print("  📝 Google Docs")
            print("  📊 Google Sheets")
            print("  ✅ Google Tasks")
            print("  📋 Google Keep")
            return True
        else:
            print("❌ Échec de l'authentification")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification : {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(init_google_auth())
    if result:
        print("\n🎉 Sylvie est prête ! Vous pouvez maintenant lui demander de vérifier vos emails.")
    else:
        print("\n⚠️  Authentification échouée. Vérifiez vos credentials Google.")
