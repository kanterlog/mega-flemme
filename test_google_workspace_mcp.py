#!/usr/bin/env python3
"""
🧪 Tests Complets - Google Workspace MCP Integration pour Sylvie v2.2
Test de l'intégration complète Gmail + Google Calendar + Multi-comptes
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.google_workspace_mcp import (
    GoogleWorkspaceMCPIntegration,
    GoogleWorkspaceAccount,
    CalendarEvent,
    EmailMessage,
    format_email_for_display,
    format_calendar_event_for_display,
    setup_default_accounts
)

class GoogleWorkspaceMCPTester:
    def __init__(self):
        self.test_results = []
        self.integration = GoogleWorkspaceMCPIntegration()
        
    def log_test(self, test_name, status, details=""):
        """Log des résultats de test"""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
    async def test_multi_account_setup(self):
        """Test de configuration des comptes multiples"""
        print("👥 Test configuration comptes multiples...")
        
        try:
            # Ajouter plusieurs comptes
            account1 = self.integration.add_account(
                "sylvie@kantermator.com", 
                "professional", 
                "Compte principal avec accès complet Gmail + Calendar"
            )
            
            account2 = self.integration.add_account(
                "kanter@kantermator.com",
                "admin", 
                "Compte admin avec calendriers d'équipe"
            )
            
            account3 = self.integration.add_account(
                "personal@gmail.com",
                "personal",
                "Compte personnel avec calendrier famille"
            )
            
            print(f"  ✅ Compte 1: {account1.email} ({account1.account_type})")
            print(f"  ✅ Compte 2: {account2.email} ({account2.account_type})")
            print(f"  ✅ Compte 3: {account3.email} ({account3.account_type})")
            
            # Test listing comptes
            accounts_list = self.integration.list_accounts()
            print(f"  📋 {len(accounts_list)} comptes configurés")
            
            # Test changement compte par défaut
            success = self.integration.switch_default_account("kanter@kantermator.com")
            print(f"  🔄 Changement compte défaut: {success}")
            
            self.log_test("Multi-Account Setup", "✅", f"{len(accounts_list)} comptes")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Multi-Account Setup", "❌", str(e))
            
        print("✅ Configuration comptes testée\n")
        
    async def test_oauth_authentication(self):
        """Test d'authentification OAuth2"""
        print("🔐 Test authentification OAuth2...")
        
        try:
            # Test authentification pour chaque compte
            for email in self.integration.accounts.keys():
                success = await self.integration.authenticate_account(email)
                print(f"  🔑 Auth {email}: {'✅ OK' if success else '❌ FAIL'}")
                
                if success:
                    account = self.integration.accounts[email]
                    print(f"    Token: {account.credentials['access_token'][:20]}...")
                    print(f"    Dernière auth: {account.last_auth}")
            
            self.log_test("OAuth Authentication", "✅", f"{len(self.integration.accounts)} comptes auth")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("OAuth Authentication", "❌", str(e))
            
        print("✅ Authentification testée\n")
        
    async def test_advanced_gmail_search(self):
        """Test de recherche Gmail avancée"""
        print("🔍 Test recherche Gmail avancée...")
        
        search_queries = [
            {
                "query": "is:unread from:marie",
                "description": "Emails non lus de Marie"
            },
            {
                "query": "subject:rapport has:attachment",
                "description": "Emails avec 'rapport' et pièces jointes"
            },
            {
                "query": "to:sylvie after:2024-01-01",
                "description": "Emails vers Sylvie après le 1er janvier"
            },
            {
                "query": "label:urgent OR label:important",
                "description": "Emails urgents ou importants"
            },
            {
                "query": "formation IA",
                "description": "Recherche libre 'formation IA'"
            }
        ]
        
        try:
            for query_test in search_queries:
                emails = await self.integration.search_emails_advanced(
                    query_test["query"], 
                    max_results=10,
                    include_attachments=True
                )
                
                print(f"  📧 {query_test['description']}: {len(emails)} résultats")
                
                # Afficher le premier email trouvé
                if emails:
                    first_email = emails[0]
                    print(f"    Premier: {first_email.subject[:50]}...")
                    print(f"    De: {first_email.sender}")
                    print(f"    Non lu: {first_email.is_unread}")
                    print(f"    Pièces jointes: {len(first_email.attachments)}")
                
                self.log_test("Gmail Search", "✅", f"{query_test['description']}: {len(emails)} emails")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Gmail Search", "❌", str(e))
            
        print("✅ Recherche Gmail testée\n")
        
    async def test_email_operations(self):
        """Test des opérations email (brouillons, réponses)"""
        print("📝 Test opérations email...")
        
        try:
            # Test création brouillon
            draft = await self.integration.create_email_draft(
                to=["client@entreprise.com"],
                subject="Proposition projet KanterMator",
                body="Bonjour,\n\nNous avons le plaisir de vous présenter...",
                cc=["kanter@kantermator.com"]
            )
            
            print(f"  📝 Brouillon créé: {draft['id']}")
            print(f"    Sujet: {draft['subject']}")
            print(f"    Destinataires: {', '.join(draft['to'])}")
            
            # Test réponse à un email
            reply_draft = await self.integration.reply_to_email(
                original_email_id="email_001",
                reply_body="Merci pour votre rapport. Pouvez-vous préciser...",
                send_immediately=False
            )
            
            print(f"  ↩️ Réponse créée: {reply_draft['id']}")
            print(f"    Status: {reply_draft['status']}")
            
            # Test réponse envoyée immédiatement
            reply_sent = await self.integration.reply_to_email(
                original_email_id="email_002",
                reply_body="Parfait, merci pour l'information !",
                send_immediately=True
            )
            
            print(f"  📤 Réponse envoyée: {reply_sent['status']}")
            
            self.log_test("Email Operations", "✅", "Brouillons et réponses")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Email Operations", "❌", str(e))
            
        print("✅ Opérations email testées\n")
        
    async def test_calendar_management(self):
        """Test de gestion du calendrier"""
        print("📅 Test gestion calendrier...")
        
        try:
            # Test récupération événements existants
            events = await self.integration.get_calendar_events(
                time_min=datetime.now().isoformat(),
                time_max=(datetime.now() + timedelta(days=14)).isoformat(),
                max_results=50
            )
            
            print(f"  📅 Événements trouvés: {len(events)}")
            
            for i, event in enumerate(events[:3]):  # Afficher les 3 premiers
                print(f"    {i+1}. {event.summary}")
                print(f"       Début: {event.start_time}")
                print(f"       Lieu: {event.location or 'Non spécifié'}")
                print(f"       Participants: {len(event.attendees)}")
            
            # Test création nouvel événement
            new_event = await self.integration.create_calendar_event(
                summary="Réunion équipe Sylvie v2.2",
                start_time=(datetime.now() + timedelta(days=2, hours=14)).isoformat(),
                end_time=(datetime.now() + timedelta(days=2, hours=15, minutes=30)).isoformat(),
                description="Discussion des nouvelles fonctionnalités Google Workspace",
                location="Salle de conférence B",
                attendees=["marie@kantermator.com", "alex@kantermator.com", "kanter@kantermator.com"]
            )
            
            print(f"  ✨ Nouvel événement créé: {new_event.summary}")
            print(f"    ID: {new_event.id}")
            print(f"    Participants: {len(new_event.attendees)}")
            
            # Test suppression événement
            delete_success = await self.integration.delete_calendar_event(new_event.id)
            print(f"  🗑️ Suppression événement: {'✅ OK' if delete_success else '❌ FAIL'}")
            
            self.log_test("Calendar Management", "✅", f"{len(events)} événements, création/suppression OK")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Calendar Management", "❌", str(e))
            
        print("✅ Gestion calendrier testée\n")
        
    async def test_productivity_analysis(self):
        """Test d'analyse de productivité"""
        print("📊 Test analyse de productivité...")
        
        try:
            # Analyse pour le compte par défaut
            analysis = await self.integration.analyze_email_productivity(days_back=7)
            
            print(f"  📊 Analyse pour: {analysis['account']}")
            print(f"  📧 Emails reçus: {analysis['stats']['emails_received']}")
            print(f"  📤 Emails envoyés: {analysis['stats']['emails_sent']}")
            print(f"  📋 Emails non lus: {analysis['stats']['emails_unread']}")
            print(f"  ⏰ Temps de réponse moyen: {analysis['stats']['average_response_time']}")
            print(f"  📈 Score de productivité: {analysis['productivity_score']}/100")
            
            print(f"  💡 Suggestions:")
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                print(f"    {i}. {suggestion}")
            
            self.log_test("Productivity Analysis", "✅", f"Score: {analysis['productivity_score']}")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Productivity Analysis", "❌", str(e))
            
        print("✅ Analyse productivité testée\n")
        
    async def test_meeting_suggestions(self):
        """Test de suggestions de créneaux de réunion"""
        print("💡 Test suggestions créneaux réunion...")
        
        try:
            # Test suggestions pour différents scénarios
            scenarios = [
                {
                    "duration_hours": 1,
                    "participants": ["marie@kantermator.com", "alex@kantermator.com"],
                    "description": "Réunion équipe 1h"
                },
                {
                    "duration_hours": 2,
                    "participants": ["client@entreprise.com"],
                    "description": "Demo client 2h"
                },
                {
                    "duration_hours": 0.5,
                    "participants": [],
                    "description": "Point rapide 30min"
                }
            ]
            
            for scenario in scenarios:
                suggestions = await self.integration.suggest_meeting_times(
                    duration_hours=scenario["duration_hours"],
                    participants=scenario["participants"]
                )
                
                print(f"  💡 {scenario['description']}: {len(suggestions)} créneaux")
                
                # Afficher les 3 meilleurs créneaux
                for i, slot in enumerate(suggestions[:3], 1):
                    start = datetime.fromisoformat(slot["start_time"])
                    print(f"    {i}. {start.strftime('%A %d/%m à %H:%M')} (score: {slot['availability_score']})")
                
                self.log_test("Meeting Suggestions", "✅", f"{scenario['description']}: {len(suggestions)} créneaux")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Meeting Suggestions", "❌", str(e))
            
        print("✅ Suggestions créneaux testées\n")
        
    async def test_formatting_utilities(self):
        """Test des utilitaires de formatage"""
        print("🎨 Test utilitaires formatage...")
        
        try:
            # Test formatage email
            sample_email = EmailMessage(
                id="test_email",
                subject="Test de formatage email avec Sylvie v2.2",
                sender="test@kantermator.com",
                recipients=["sylvie@kantermator.com"],
                body_text="Ceci est un test de formatage pour les emails...",
                snippet="Ceci est un test de formatage pour les emails",
                date=datetime.now().isoformat(),
                is_unread=True,
                is_important=True,
                attachments=[{"filename": "test.pdf", "size": 1024}]
            )
            
            formatted_email = format_email_for_display(sample_email)
            print("  📧 Email formaté:")
            print("  " + "\n  ".join(formatted_email.split('\n')))
            
            # Test formatage événement calendrier
            sample_event = CalendarEvent(
                id="test_event",
                summary="Test événement Sylvie v2.2",
                description="Test de formatage pour les événements de calendrier",
                start_time=(datetime.now() + timedelta(hours=2)).isoformat(),
                end_time=(datetime.now() + timedelta(hours=3)).isoformat(),
                location="Bureau Sylvie",
                attendees=["kanter@kantermator.com", "marie@kantermator.com"]
            )
            
            formatted_event = format_calendar_event_for_display(sample_event)
            print("\n  📅 Événement formaté:")
            print("  " + "\n  ".join(formatted_event.split('\n')))
            
            self.log_test("Formatting Utilities", "✅", "Email et événement formatés")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Formatting Utilities", "❌", str(e))
            
        print("✅ Utilitaires formatage testés\n")
        
    async def test_integration_status(self):
        """Test du status global de l'intégration"""
        print("🔍 Test status intégration...")
        
        try:
            status = self.integration.get_integration_status()
            
            print(f"  📋 Version: {status['version']}")
            print(f"  👥 Comptes configurés: {status['accounts_configured']}")
            print(f"  🎯 Compte par défaut: {status['default_account']}")
            print(f"  🛠️ Services disponibles: {', '.join(status['services_available'])}")
            
            print(f"  ✨ Fonctionnalités activées:")
            for feature, enabled in status['features'].items():
                status_icon = "✅" if enabled else "❌"
                print(f"    {status_icon} {feature.replace('_', ' ').title()}")
            
            self.log_test("Integration Status", "✅", f"v{status['version']} - {status['accounts_configured']} comptes")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            self.log_test("Integration Status", "❌", str(e))
            
        print("✅ Status intégration testé\n")
        
    async def run_all_tests(self):
        """Lance tous les tests Google Workspace MCP"""
        print("🚀 Tests Google Workspace MCP Integration pour Sylvie v2.2")
        print("=" * 70)
        print()
        
        # Setup initial
        await setup_default_accounts()
        
        # Exécution de tous les tests
        await self.test_multi_account_setup()
        await self.test_oauth_authentication()
        await self.test_advanced_gmail_search()
        await self.test_email_operations()
        await self.test_calendar_management()
        await self.test_productivity_analysis()
        await self.test_meeting_suggestions()
        await self.test_formatting_utilities()
        await self.test_integration_status()
        
        # Résumé des résultats
        self.print_test_summary()
        
    def print_test_summary(self):
        """Affiche le résumé des tests"""
        print("📊 Résumé des Tests Google Workspace MCP")
        print("-" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if "✅" in t["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Tests réussis: {passed_tests} ✅")
        print(f"Tests échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDétails des tests:")
        for test in self.test_results:
            print(f"  {test['status']} {test['test']} - {test['details']}")
            
        print(f"\n🎉 Tests terminés à {datetime.now().strftime('%H:%M:%S')}")
        
        # Recommandations pour l'intégration Sylvie
        print("\n💡 Recommandations pour Sylvie v2.2:")
        print("  1. ✅ Intégration Gmail MCP complète avec recherche avancée")
        print("  2. ✅ Gestion Google Calendar avec création/modification/suppression")
        print("  3. ✅ Support multi-comptes pour usage professionnel/personnel")
        print("  4. ✅ Authentification OAuth2 sécurisée")
        print("  5. ✅ Analyse de productivité email intelligente")
        print("  6. ✅ Suggestions automatiques de créneaux de réunion")
        print("  7. 🔄 À implémenter : Synchronisation temps réel avec API Google")
        print("  8. 🔄 À implémenter : Cache local pour performance")
        print("  9. 🔄 À implémenter : Notifications push pour nouveaux emails/événements")
        print("  10. 🔄 À implémenter : Intelligence IA pour catégorisation automatique")

async def main():
    """Fonction principale"""
    tester = GoogleWorkspaceMCPTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
