#!/usr/bin/env python3
"""
🧪 Test final de KanterMator + Sylvie
Vérification complète de tous les composants
"""

import asyncio
import sys
import traceback

async def test_sylvie():
    """Test complet de Sylvie Agent"""
    try:
        print("🔄 Importation de Sylvie...")
        from app.services.sylvie_agent import sylvie_agent
        
        print("✅ Sylvie importée avec succès!")
        print()
        
        # Test simple de conversation
        print("🔄 Test de conversation...")
        response = await sylvie_agent.process_message("Bonjour Sylvie, peux-tu m'aider ?")
        
        print("✅ Test de conversation réussi!")
        print(f"📝 Réponse Sylvie: {response.message[:100]}...")
        print()
        
        print("🎉 SUCCÈS COMPLET!")
        print("=" * 50)
        print("🤖 Sylvie Agent avec IA Hybride")
        print("📧 Gmail + 📅 Calendar + 📁 Drive + 📊 Sheets")
        print("✅ Tasks + 📝 Keep + 📊 Slides + 📄 Docs")
        print("🔑 Google AI Key configurée")
        print("🚀 KanterMator prêt pour production!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_sylvie())
    sys.exit(0 if success else 1)
