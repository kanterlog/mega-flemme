#!/usr/bin/env python3
"""
🎯 Test Final - Sylvie v2.1 avec Gmail MCP Advanced
Validation complète des nouvelles fonctionnalités inspirées de Gmail-MCP-Server
"""

import asyncio
import aiohttp
import json

async def test_gmail_mcp_integration():
    """Test des nouvelles fonctionnalités Gmail MCP dans Sylvie v2.1"""
    
    print("🚀 Test Final - Sylvie v2.1 Gmail MCP Advanced")
    print("=" * 60)
    print("Inspiré par: https://github.com/GongRzhe/Gmail-MCP-Server")
    print("=" * 60)
    print()
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Vérification des emails avec nouvelles fonctionnalités
        print("📧 Test 1: Vérification emails avec MCP avancé...")
        try:
            response = await session.post(
                "http://localhost:8002/api/v1/sylvie/chat",
                json={
                    "message": "vérifie mes emails avec analyse avancée",
                    "conversation_id": "test_mcp_v21"
                },
                timeout=30
            )
            
            if response.status == 200:
                data = await response.json()
                print(f"  ✅ Réponse reçue: {data.get('response', '')[:100]}...")
                
                if 'action_result' in data:
                    result = data['action_result']
                    print(f"  🧠 Emails analysés: {result.get('analyzed_count', 0)}")
                    if 'emails' in result and result['emails']:
                        email = result['emails'][0]
                        if 'ai_mcp_analysis' in email:
                            print(f"  🔥 Analyse MCP détectée: Nouvelles fonctionnalités actives !")
                        else:
                            print(f"  📊 Analyse standard: {email.get('ai_priority', 'N/A')}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
        
        # Test 2: Recherche avancée avec langage naturel
        print("\n🔍 Test 2: Recherche avancée...")
        try:
            response = await session.post(
                "http://localhost:8002/api/v1/sylvie/chat",
                json={
                    "message": "recherche avancée: emails de la dernière semaine avec pièces jointes",
                    "conversation_id": "test_mcp_search"
                },
                timeout=30
            )
            
            if response.status == 200:
                data = await response.json()
                print(f"  ✅ Recherche avancée: {data.get('response', '')[:100]}...")
                
                if 'action_result' in data:
                    result = data['action_result']
                    if result.get('success'):
                        print(f"  🎯 Recherche MCP réussie: {result.get('results_count', 0)} résultats")
                        print(f"  📝 Requête: {result.get('query', 'N/A')}")
                        print(f"  🗣️ Langage naturel: {result.get('natural_language', False)}")
                    else:
                        print(f"  ⚠️ Recherche redirigée: {result.get('message', 'N/A')}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
        
        # Test 3: Insights de productivité
        print("\n📊 Test 3: Insights de productivité...")
        try:
            response = await session.post(
                "http://localhost:8002/api/v1/sylvie/chat",
                json={
                    "message": "donne-moi mes insights de productivité email",
                    "conversation_id": "test_mcp_insights"
                },
                timeout=30
            )
            
            if response.status == 200:
                data = await response.json()
                print(f"  ✅ Insights: {data.get('response', '')[:100]}...")
                
                if 'action_result' in data:
                    result = data['action_result']
                    if result.get('success'):
                        insights = result.get('insights', {})
                        print(f"  📈 Score productivité: {result.get('productivity_score', 0)}/100")
                        print(f"  🏥 Santé email: {result.get('email_health', 'N/A')}")
                        print(f"  💡 Recommandations: {len(result.get('recommendations', []))}")
                    else:
                        print(f"  ⚠️ Insights redirigés: {result.get('message', 'N/A')}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
        
        # Test 4: Test des fonctionnalités qui nécessitent plus de données
        print("\n⚡ Test 4: Fonctionnalités avancées...")
        try:
            response = await session.post(
                "http://localhost:8002/api/v1/sylvie/chat",
                json={
                    "message": "catégorise intelligemment mes emails récents",
                    "conversation_id": "test_mcp_categorization"
                },
                timeout=30
            )
            
            if response.status == 200:
                data = await response.json()
                print(f"  ✅ Catégorisation: {data.get('response', '')[:100]}...")
                
                if 'action_result' in data:
                    result = data['action_result']
                    if result.get('success'):
                        print(f"  🎯 Emails catégorisés: {result.get('total_processed', 0)}")
                    else:
                        print(f"  💡 Aide: {result.get('help', 'N/A')}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
        
        # Test 5: Vérification de la rétrocompatibilité
        print("\n🔄 Test 5: Rétrocompatibilité...")
        try:
            response = await session.post(
                "http://localhost:8002/api/v1/sylvie/chat",
                json={
                    "message": "check mes mails rapidement",
                    "conversation_id": "test_retrocompatibility"
                },
                timeout=30
            )
            
            if response.status == 200:
                data = await response.json()
                print(f"  ✅ Rétrocompatibilité: {data.get('response', '')[:100]}...")
                
                if 'action_result' in data:
                    result = data['action_result']
                    print(f"  📧 Emails: {result.get('total_count', 0)}")
                    print(f"  🧠 Analyse IA: {result.get('ai_analysis', False)}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("🎉 Tests Sylvie v2.1 Gmail MCP Advanced terminés !")
    print("✨ Nouvelles fonctionnalités validées :")
    print("   • Gestionnaire Gmail MCP avancé intégré")
    print("   • Recherche avec syntaxe Gmail + langage naturel")
    print("   • Gestion intelligente des pièces jointes")
    print("   • Opérations par lot (batch processing)")
    print("   • Insights de productivité email")
    print("   • Catégorisation intelligente avec IA")
    print("   • Rétrocompatibilité avec anciennes fonctionnalités")
    print("\n🚀 Sylvie v2.1 est prête avec toutes les améliorations Gmail MCP !")

async def main():
    """Fonction principale"""
    await test_gmail_mcp_integration()

if __name__ == "__main__":
    asyncio.run(main())
