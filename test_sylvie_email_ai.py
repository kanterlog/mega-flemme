#!/usr/bin/env python3
"""
🎯 Test Final - Sylvie v2.0 avec Email IA Avancé
Validation complète de l'intégration des fonctionnalités email intelligentes
"""

import asyncio
import json
import aiohttp
from datetime import datetime

class SylvieEmailAITester:
    def __init__(self):
        self.base_url = "http://localhost:8002/api/v1/sylvie"
        self.test_results = []
        
    async def test_smart_email_check(self):
        """Test de vérification intelligente des emails"""
        print("📧 Test vérification emails intelligente...")
        
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": "check mes mails avec analyse IA",
                        "conversation_id": "test_email_ai"
                    },
                    timeout=30
                )
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ Réponse reçue: {data.get('response', '')[:100]}...")
                    
                    # Vérification des métadonnées IA
                    if 'action_result' in data and data['action_result']:
                        result = data['action_result']
                        if 'ai_analysis' in result:
                            print(f"  🧠 Analyse IA activée: {result.get('analyzed_count', 0)} emails analysés")
                            print(f"  🔥 Emails urgents: {result.get('urgent_count', 0)}")
                            print(f"  📅 Demandes réunion: {result.get('meeting_requests', 0)}")
                            return True
                    
                    print("  ⚠️ Pas d'analyse IA détectée dans la réponse")
                    return False
                else:
                    print(f"  ❌ Erreur HTTP: {response.status}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Erreur: {str(e)}")
                return False
                
    async def test_email_summary_ai(self):
        """Test de résumé intelligent des emails"""
        print("\n📊 Test résumé emails avec IA...")
        
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": "fais-moi un résumé intelligent de mes emails",
                        "conversation_id": "test_summary_ai"
                    },
                    timeout=30
                )
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ Résumé généré: {data.get('response', '')[:150]}...")
                    
                    if 'action_result' in data and data['action_result']:
                        result = data['action_result']
                        if 'statistics' in result:
                            stats = result['statistics']
                            print(f"  📈 Stats: {stats.get('total_emails', 0)} emails, {stats.get('urgent_emails', 0)} urgents")
                            print(f"  💼 Business: {stats.get('business_inquiries', 0)}, Réunions: {stats.get('meeting_requests', 0)}")
                            return True
                    
                    print("  ⚠️ Pas de statistiques IA dans la réponse")
                    return False
                else:
                    print(f"  ❌ Erreur HTTP: {response.status}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Erreur: {str(e)}")
                return False
                
    async def test_urgent_emails_detection(self):
        """Test de détection des emails urgents"""
        print("\n🔥 Test détection emails urgents...")
        
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": "montre-moi mes emails urgents",
                        "conversation_id": "test_urgent_ai"
                    },
                    timeout=30
                )
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ Réponse urgents: {data.get('response', '')[:100]}...")
                    
                    if 'action_result' in data and data['action_result']:
                        result = data['action_result']
                        if 'action' in result and result['action'] == 'urgent_emails':
                            print(f"  🎯 Action urgents détectée: {len(result.get('data', []))} emails")
                            return True
                        elif result.get('action') == 'no_urgent_emails':
                            print(f"  ✅ Aucun email urgent détecté (normal)")
                            return True
                    
                    print("  ⚠️ Action urgents non détectée")
                    return False
                else:
                    print(f"  ❌ Erreur HTTP: {response.status}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Erreur: {str(e)}")
                return False
                
    async def test_natural_language_understanding(self):
        """Test de compréhension du langage naturel"""
        print("\n🗣️ Test compréhension langage naturel...")
        
        test_phrases = [
            "regarde si j'ai reçu quelque chose d'important",
            "vérifie ma boîte mail s'il te plaît",
            "y a-t-il des messages urgents ?",
            "mes emails du jour",
            "check mes mails rapidement"
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for phrase in test_phrases:
                try:
                    print(f"  Test: '{phrase}'")
                    
                    response = await session.post(
                        f"{self.base_url}/chat",
                        json={
                            "message": phrase,
                            "conversation_id": f"test_nl_{hash(phrase)}"
                        },
                        timeout=20
                    )
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Vérification que Sylvie comprend que c'est une demande email
                        response_text = data.get('response', '').lower()
                        if any(word in response_text for word in ['email', 'mail', 'message', 'boîte']):
                            print(f"    ✅ Comprise comme demande email")
                            success_count += 1
                        else:
                            print(f"    ⚠️ Pas reconnue comme demande email")
                    else:
                        print(f"    ❌ Erreur HTTP: {response.status}")
                        
                except Exception as e:
                    print(f"    ❌ Erreur: {str(e)}")
                
                await asyncio.sleep(1)  # Pause entre les tests
        
        print(f"  📊 Résultat: {success_count}/{len(test_phrases)} phrases comprises")
        return success_count >= len(test_phrases) * 0.7  # 70% de réussite minimum
        
    async def test_ai_integration_status(self):
        """Test du statut d'intégration IA"""
        print("\n🧠 Test statut intégration IA...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test avec une phrase spécifique pour déclencher l'IA email
                response = await session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": "analyse mes emails avec l'intelligence artificielle",
                        "conversation_id": "test_ai_status"
                    },
                    timeout=25
                )
                
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '')
                    
                    # Vérification des indicateurs d'IA avancée
                    ai_indicators = [
                        'analyse', 'intelligent', 'priorité', 'catégorie', 
                        'urgent', 'IA', 'intelligence artificielle'
                    ]
                    
                    found_indicators = [ind for ind in ai_indicators if ind.lower() in response_text.lower()]
                    
                    print(f"  ✅ Réponse générée avec indicateurs IA: {found_indicators}")
                    
                    if len(found_indicators) >= 2:
                        print(f"  🎯 IA email avancée confirmée")
                        return True
                    else:
                        print(f"  ⚠️ IA basique détectée")
                        return False
                else:
                    print(f"  ❌ Erreur HTTP: {response.status}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Erreur: {str(e)}")
                return False
    
    async def run_all_tests(self):
        """Lance tous les tests"""
        print("🚀 Tests Sylvie v2.0 - Email IA Avancé")
        print("=" * 60)
        print()
        
        tests = [
            ("Vérification emails intelligente", self.test_smart_email_check),
            ("Résumé emails avec IA", self.test_email_summary_ai),
            ("Détection emails urgents", self.test_urgent_emails_detection),
            ("Compréhension langage naturel", self.test_natural_language_understanding),
            ("Statut intégration IA", self.test_ai_integration_status)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                success = await test_func()
                results.append((test_name, success))
                self.test_results.append({
                    "test": test_name,
                    "success": success,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            except Exception as e:
                print(f"\n❌ Erreur dans {test_name}: {str(e)}")
                results.append((test_name, False))
        
        # Résumé final
        self.print_final_summary(results)
        
    def print_final_summary(self, results):
        """Affiche le résumé final des tests"""
        print(f"\n🎯 Résumé Final - Tests Sylvie v2.0 Email IA")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r[1]])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total tests: {total_tests}")
        print(f"Tests réussis: {passed_tests}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        print(f"\nDétail des résultats:")
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
        
        print(f"\n🕒 Tests terminés à {datetime.now().strftime('%H:%M:%S')}")
        
        # Évaluation globale
        if success_rate >= 80:
            print(f"\n🎉 EXCELLENT ! Sylvie v2.0 Email IA est opérationnelle")
            print("✨ Nouvelles fonctionnalités validées:")
            print("   • Analyse intelligente des emails")
            print("   • Détection automatique de priorité")
            print("   • Catégorisation avancée")
            print("   • Résumés intelligents")
            print("   • Compréhension langage naturel")
        elif success_rate >= 60:
            print(f"\n👍 BIEN ! Sylvie v2.0 fonctionne avec quelques améliorations possibles")
        else:
            print(f"\n⚠️ ATTENTION ! Des ajustements sont nécessaires")

async def main():
    """Fonction principale"""
    tester = SylvieEmailAITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
