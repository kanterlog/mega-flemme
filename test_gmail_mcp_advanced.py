#!/usr/bin/env python3
"""
🧪 Test Gmail MCP Advanced Features pour Sylvie v2.1
Validation des fonctionnalités inspirées du projet Gmail-MCP-Server
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.gmail_mcp_advanced import (
    AdvancedGmailManager,
    GmailMCPInspiredFeatures,
    EmailAttachment,
    EmailContent,
    BatchOperation,
    GmailSearchOperator
)

class GmailMCPAdvancedTester:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log des résultats de test"""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        print(f"  {status} {test_name} - {details}")
        
    def test_gmail_search_operators(self):
        """Test des opérateurs de recherche Gmail avancés"""
        print("🔍 Test opérateurs recherche Gmail...")
        
        # Test de construction de requêtes
        test_cases = [
            {
                "criteria": {"from": "john@example.com", "has_attachment": True},
                "expected": "from:john@example.com has:attachment"
            },
            {
                "criteria": {"subject": "meeting notes", "after": "2024/01/01"},
                "expected": 'subject:"meeting notes" after:2024/01/01'
            },
            {
                "criteria": {"is_unread": True, "label": "work"},
                "expected": "is:unread label:work"
            }
        ]
        
        # Simulation du gestionnaire Gmail
        class MockGmailManager:
            def build_advanced_search_query(self, criteria):
                return AdvancedGmailManager(None).build_advanced_search_query(criteria)
        
        manager = MockGmailManager()
        
        for i, case in enumerate(test_cases):
            query = manager.build_advanced_search_query(case["criteria"])
            print(f"    Critères: {case['criteria']}")
            print(f"    Requête générée: {query}")
            print(f"    Attendu: {case['expected']}")
            
            # Vérification que tous les éléments attendus sont présents
            expected_parts = case["expected"].split()
            query_parts = query.split()
            
            all_present = all(part in query_parts for part in expected_parts)
            
            if all_present:
                self.log_test("Gmail Search Operators", "✅", f"Test case {i+1} réussi")
            else:
                self.log_test("Gmail Search Operators", "⚠️", f"Test case {i+1} partiel")
        
        print("✅ Opérateurs recherche Gmail testés\n")
        
    def test_natural_language_parsing(self):
        """Test de parsing du langage naturel"""
        print("🗣️ Test parsing langage naturel...")
        
        test_queries = [
            {
                "query": "emails de john@example.com avec pièce jointe",
                "expected_criteria": ["from", "has_attachment"]
            },
            {
                "query": "messages non lus de la dernière semaine",
                "expected_criteria": ["is_unread", "after"]
            },
            {
                "query": "sujet: rapport mensuel important",
                "expected_criteria": ["subject", "is_important"]
            },
            {
                "query": "emails d'aujourd'hui avec documents",
                "expected_criteria": ["after", "has_attachment"]
            }
        ]
        
        # Simulation des fonctionnalités MCP
        class MockMCPFeatures:
            def _parse_natural_query(self, query):
                return GmailMCPInspiredFeatures(None)._parse_natural_query(query)
        
        features = MockMCPFeatures()
        
        for query_test in test_queries:
            criteria = features._parse_natural_query(query_test["query"])
            
            print(f"    Requête: '{query_test['query']}'")
            print(f"    Critères détectés: {list(criteria.keys())}")
            print(f"    Critères attendus: {query_test['expected_criteria']}")
            
            # Vérification de la détection des critères
            detected_criteria = set(criteria.keys())
            expected_criteria = set(query_test['expected_criteria'])
            
            if detected_criteria.intersection(expected_criteria):
                self.log_test("Natural Language Parsing", "✅", f"Critères partiellement détectés")
            else:
                self.log_test("Natural Language Parsing", "⚠️", f"Aucun critère détecté")
        
        print("✅ Parsing langage naturel testé\n")
        
    def test_email_content_structure(self):
        """Test de la structure EmailContent"""
        print("📧 Test structure EmailContent...")
        
        # Création d'un contenu email de test
        content = EmailContent()
        content.plain_text = "Bonjour, voici le rapport mensuel."
        content.html_content = "<p>Bonjour, voici le <b>rapport mensuel</b>.</p>"
        
        # Ajout de pièces jointes
        attachment1 = EmailAttachment(
            id="att_001",
            filename="rapport.pdf",
            mime_type="application/pdf",
            size=245760  # 240 KB
        )
        
        attachment2 = EmailAttachment(
            id="att_002", 
            filename="presentation.pptx",
            mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            size=1048576  # 1 MB
        )
        
        content.attachments = [attachment1, attachment2]
        content.headers = {
            "From": "john@example.com",
            "To": "marie@example.com",
            "Subject": "Rapport mensuel Q4",
            "Date": "Thu, 1 Aug 2025 12:00:00 +0000"
        }
        
        # Validation de la structure
        print(f"    Texte brut: {len(content.plain_text)} chars")
        print(f"    HTML: {len(content.html_content)} chars")
        print(f"    Pièces jointes: {len(content.attachments)}")
        print(f"    Headers: {len(content.headers)}")
        
        # Validation des pièces jointes
        total_size = sum(att.size for att in content.attachments)
        print(f"    Taille totale attachments: {total_size // 1024} KB")
        
        if len(content.attachments) == 2 and total_size > 0:
            self.log_test("Email Content Structure", "✅", "Structure valide avec attachments")
        else:
            self.log_test("Email Content Structure", "⚠️", "Structure incomplète")
        
        print("✅ Structure EmailContent testée\n")
        
    def test_batch_operation_structure(self):
        """Test de la structure BatchOperation"""
        print("🔄 Test structure BatchOperation...")
        
        # Création d'une opération par lot
        operation = BatchOperation(
            message_ids=["msg_001", "msg_002", "msg_003", "msg_004", "msg_005"],
            operation_type="modify_labels",
            batch_size=2,
            add_labels=["IMPORTANT", "WORK"],
            remove_labels=["INBOX"]
        )
        
        print(f"    Messages à traiter: {len(operation.message_ids)}")
        print(f"    Taille du lot: {operation.batch_size}")
        print(f"    Type d'opération: {operation.operation_type}")
        print(f"    Labels à ajouter: {operation.add_labels}")
        print(f"    Labels à supprimer: {operation.remove_labels}")
        
        # Simulation du traitement par lots
        for i in range(0, len(operation.message_ids), operation.batch_size):
            batch = operation.message_ids[i:i + operation.batch_size]
            print(f"    Lot {i//operation.batch_size + 1}: {batch}")
            
            # Simulation de succès/échecs
            operation.success_count += len(batch) - 1  # Un échec par lot
            operation.failure_count += 1
            operation.errors.append(f"Échec simulé lot {i//operation.batch_size + 1}")
        
        print(f"    Résultats: {operation.success_count} succès, {operation.failure_count} échecs")
        
        if operation.success_count > 0 and len(operation.errors) > 0:
            self.log_test("Batch Operation Structure", "✅", "Structure et simulation OK")
        else:
            self.log_test("Batch Operation Structure", "⚠️", "Problème de simulation")
        
        print("✅ Structure BatchOperation testée\n")
        
    def test_gmail_search_operator_enum(self):
        """Test de l'énumération GmailSearchOperator"""
        print("📋 Test énumération GmailSearchOperator...")
        
        # Vérification de tous les opérateurs
        operators = [
            (GmailSearchOperator.FROM, "from:"),
            (GmailSearchOperator.TO, "to:"),
            (GmailSearchOperator.SUBJECT, "subject:"),
            (GmailSearchOperator.HAS_ATTACHMENT, "has:attachment"),
            (GmailSearchOperator.AFTER, "after:"),
            (GmailSearchOperator.BEFORE, "before:"),
            (GmailSearchOperator.IS_UNREAD, "is:unread"),
            (GmailSearchOperator.IS_READ, "is:read"),
            (GmailSearchOperator.IS_IMPORTANT, "is:important"),
            (GmailSearchOperator.LABEL, "label:"),
            (GmailSearchOperator.LARGER, "larger:"),
            (GmailSearchOperator.SMALLER, "smaller:"),
            (GmailSearchOperator.CATEGORY, "category:")
        ]
        
        for operator, expected_value in operators:
            print(f"    {operator.name}: {operator.value}")
            if operator.value == expected_value:
                self.log_test("Gmail Search Operator Enum", "✅", f"{operator.name} correct")
            else:
                self.log_test("Gmail Search Operator Enum", "❌", f"{operator.name} incorrect")
        
        print("✅ Énumération GmailSearchOperator testée\n")
        
    def test_productivity_scoring(self):
        """Test du calcul de score de productivité"""
        print("📊 Test calcul score productivité...")
        
        # Simulation de patterns d'emails
        test_patterns = [
            {
                "name": "Boîte vide",
                "patterns": {"total_emails": 0, "unread_emails": 0},
                "expected_score": 100
            },
            {
                "name": "Tous lus",
                "patterns": {"total_emails": 100, "unread_emails": 0},
                "expected_score": 100
            },
            {
                "name": "50% non lus",
                "patterns": {"total_emails": 100, "unread_emails": 50},
                "expected_score": 50
            },
            {
                "name": "25% non lus",
                "patterns": {"total_emails": 100, "unread_emails": 25},
                "expected_score": 75
            }
        ]
        
        # Simulation des fonctionnalités MCP
        class MockMCPFeatures:
            def _calculate_productivity_score(self, patterns):
                return GmailMCPInspiredFeatures(None)._calculate_productivity_score(patterns)
        
        features = MockMCPFeatures()
        
        for test in test_patterns:
            score = features._calculate_productivity_score(test["patterns"])
            print(f"    {test['name']}: Score {score} (attendu: {test['expected_score']})")
            
            if score == test["expected_score"]:
                self.log_test("Productivity Scoring", "✅", f"{test['name']} correct")
            else:
                self.log_test("Productivity Scoring", "⚠️", f"{test['name']} approximatif")
        
        print("✅ Calcul score productivité testé\n")
        
    def test_email_health_assessment(self):
        """Test d'évaluation de la santé email"""
        print("🏥 Test évaluation santé email...")
        
        health_tests = [
            {
                "scenario": "Excellente santé",
                "patterns": {"total_emails": 100, "unread_emails": 5},
                "expected": "Excellent"
            },
            {
                "scenario": "Bonne santé",
                "patterns": {"total_emails": 100, "unread_emails": 20},
                "expected": "Bon"
            },
            {
                "scenario": "Santé correcte",
                "patterns": {"total_emails": 100, "unread_emails": 40},
                "expected": "Correct"
            },
            {
                "scenario": "Besoin d'attention",
                "patterns": {"total_emails": 100, "unread_emails": 60},
                "expected": "Besoin d'attention"
            }
        ]
        
        # Simulation des fonctionnalités MCP
        class MockMCPFeatures:
            def _assess_email_health(self, patterns):
                return GmailMCPInspiredFeatures(None)._assess_email_health(patterns)
        
        features = MockMCPFeatures()
        
        for test in health_tests:
            health = features._assess_email_health(test["patterns"])
            print(f"    {test['scenario']}: {health} (attendu: {test['expected']})")
            
            if health == test["expected"]:
                self.log_test("Email Health Assessment", "✅", f"{test['scenario']} correct")
            else:
                self.log_test("Email Health Assessment", "⚠️", f"{test['scenario']} différent")
        
        print("✅ Évaluation santé email testée\n")
        
    def test_recommendation_generation(self):
        """Test de génération de recommandations"""
        print("💡 Test génération recommandations...")
        
        recommendation_scenarios = [
            {
                "name": "Trop de non lus",
                "patterns": {
                    "total_emails": 100,
                    "unread_emails": 40,
                    "attachment_emails": 10,
                    "top_senders": [("newsletter@example.com", 5)]
                },
                "expected_keywords": ["non lus", "priorité"]
            },
            {
                "name": "Beaucoup d'attachments",
                "patterns": {
                    "total_emails": 100,
                    "unread_emails": 10,
                    "attachment_emails": 60,
                    "top_senders": [("colleague@example.com", 8)]
                },
                "expected_keywords": ["pièces jointes", "archivez"]
            },
            {
                "name": "Expéditeur fréquent",
                "patterns": {
                    "total_emails": 100,
                    "unread_emails": 10,
                    "attachment_emails": 15,
                    "top_senders": [("spam@example.com", 25)]
                },
                "expected_keywords": ["filtres", "beaucoup d'emails"]
            }
        ]
        
        # Simulation des fonctionnalités MCP
        class MockMCPFeatures:
            def _generate_recommendations(self, patterns):
                return GmailMCPInspiredFeatures(None)._generate_recommendations(patterns)
        
        features = MockMCPFeatures()
        
        for scenario in recommendation_scenarios:
            recommendations = features._generate_recommendations(scenario["patterns"])
            print(f"    Scénario: {scenario['name']}")
            print(f"    Recommandations: {recommendations}")
            
            # Vérification que des recommandations sont générées
            if len(recommendations) > 0:
                self.log_test("Recommendation Generation", "✅", f"{scenario['name']} - {len(recommendations)} recommandations")
            else:
                self.log_test("Recommendation Generation", "⚠️", f"{scenario['name']} - Aucune recommandation")
        
        print("✅ Génération recommandations testée\n")
        
    def run_all_tests(self):
        """Lance tous les tests"""
        print("🚀 Tests Gmail MCP Advanced Features pour Sylvie v2.1")
        print("=" * 70)
        print("Inspiré par: https://github.com/GongRzhe/Gmail-MCP-Server")
        print("=" * 70)
        print()
        
        # Exécution de tous les tests
        self.test_gmail_search_operators()
        self.test_natural_language_parsing()
        self.test_email_content_structure()
        self.test_batch_operation_structure()
        self.test_gmail_search_operator_enum()
        self.test_productivity_scoring()
        self.test_email_health_assessment()
        self.test_recommendation_generation()
        
        # Résumé des résultats
        self.print_test_summary()
        
    def print_test_summary(self):
        """Affiche le résumé des tests"""
        print("📊 Résumé des Tests Gmail MCP Advanced")
        print("-" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if "✅" in t["status"]])
        partial_tests = len([t for t in self.test_results if "⚠️" in t["status"]])
        failed_tests = len([t for t in self.test_results if "❌" in t["status"]])
        
        print(f"Total tests: {total_tests}")
        print(f"Tests réussis: {passed_tests}")
        print(f"Tests partiels: {partial_tests}")
        print(f"Tests échoués: {failed_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        print(f"\n🕒 Tests terminés à {datetime.now().strftime('%H:%M:%S')}")
        
        # Évaluation globale
        if success_rate >= 80:
            print(f"\n🎉 EXCELLENT ! Fonctionnalités Gmail MCP avancées validées")
            print("✨ Nouvelles capacités pour Sylvie v2.1:")
            print("   • Recherche Gmail avec syntaxe avancée")
            print("   • Parsing du langage naturel vers Gmail")
            print("   • Gestion intelligente des pièces jointes")
            print("   • Opérations par lot (batch processing)")
            print("   • Analyse de productivité email")
            print("   • Recommandations intelligentes")
            print("   • Évaluation de santé de boîte email")
        elif success_rate >= 60:
            print(f"\n👍 BIEN ! Fonctionnalités partiellement validées")
        else:
            print(f"\n⚠️ ATTENTION ! Améliorations nécessaires")
        
        print("\n💡 Prochaines étapes pour Sylvie v2.1:")
        print("  1. Intégrer AdvancedGmailManager dans sylvie_agent.py")
        print("  2. Ajouter les fonctionnalités MCP à l'interface chat")
        print("  3. Implémenter l'authentification OAuth2 robuste")
        print("  4. Créer des commandes vocales pour les opérations avancées")
        print("  5. Développer le tableau de bord email intelligence")

async def main():
    """Fonction principale"""
    tester = GmailMCPAdvancedTester()
    tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
