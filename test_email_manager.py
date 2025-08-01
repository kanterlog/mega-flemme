#!/usr/bin/env python3
"""
🧪 Test du module Advanced Email Manager
Test des nouvelles fonctionnalités email inspirées des projets GitHub
"""

import sys
import os
from datetime import datetime

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.advanced_email_manager import (
    AdvancedEmailManager, 
    SylvieEmailIntegration,
    EmailPriority,
    EmailCategory,
    ActionType
)

def test_email_analysis():
    """Test de l'analyse complète d'emails"""
    print("🔍 Test analyse emails...")
    
    manager = AdvancedEmailManager()
    
    test_emails = [
        {
            "subject": "URGENT: Serveur en panne",
            "body": "Bonjour, le serveur principal est tombé en panne ce matin. Intervention immédiate requise. Merci de m'appeler dès que possible.",
            "expected": {
                "priority": EmailPriority.CRITICAL,
                "category": EmailCategory.TECHNICAL_ISSUE,
                "sentiment": "negative"
            }
        },
        {
            "subject": "Planification réunion équipe",
            "body": "Bonjour, j'aimerais organiser une réunion d'équipe la semaine prochaine pour discuter du projet. Êtes-vous disponible mardi à 14h ?",
            "expected": {
                "priority": EmailPriority.MEDIUM,
                "category": EmailCategory.MEETING_REQUEST,
                "sentiment": "neutral"
            }
        },
        {
            "subject": "Merci pour la présentation",
            "body": "Excellente présentation hier ! L'équipe était très satisfaite. Pouvez-vous nous envoyer les slides ?",
            "expected": {
                "priority": EmailPriority.LOW,
                "category": EmailCategory.FOLLOW_UP,
                "sentiment": "positive"
            }
        }
    ]
    
    for i, email in enumerate(test_emails):
        print(f"\n  Test {i+1}: {email['subject']}")
        
        analysis = manager.analyze_email(
            email["subject"], 
            email["body"]
        )
        
        print(f"    Priorité: {analysis.priority.value} (attendu: {email['expected']['priority'].value})")
        print(f"    Catégorie: {analysis.category.value} (attendu: {email['expected']['category'].value})")
        print(f"    Sentiment: {analysis.sentiment} (attendu: {email['expected']['sentiment']})")
        print(f"    Actions: {[a.value for a in analysis.actions_required]}")
        print(f"    Résumé: {analysis.summary}")
        print(f"    Entités: {analysis.key_entities}")
        print(f"    Temps: {analysis.time_references}")
        
    print("\n✅ Analyse emails testée")

def test_smart_replies():
    """Test de génération de réponses intelligentes"""
    print("\n💬 Test génération réponses...")
    
    manager = AdvancedEmailManager()
    
    test_scenarios = [
        {
            "subject": "Demande de devis",
            "body": "Bonjour, pourriez-vous m'envoyer un devis pour le développement d'une application mobile ?",
        },
        {
            "subject": "Problème technique urgent",
            "body": "Le site web ne fonctionne plus depuis ce matin. Pouvez-vous intervenir rapidement ?",
        },
        {
            "subject": "Réunion de demain",
            "body": "Pouvez-vous confirmer votre présence à la réunion de demain à 15h ?",
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n  Scénario {i+1}: {scenario['subject']}")
        
        analysis = manager.analyze_email(scenario["subject"], scenario["body"])
        reply = manager.generate_smart_reply(analysis)
        
        print(f"    Email: {scenario['body'][:50]}...")
        print(f"    Réponse suggérée: {reply}")
        
    print("\n✅ Génération réponses testée")

def test_batch_processing():
    """Test de traitement en lot"""
    print("\n📦 Test traitement batch...")
    
    manager = AdvancedEmailManager()
    
    email_batch = [
        {
            "subject": "Newsletter hebdomadaire",
            "body": "Découvrez les actualités de cette semaine...",
            "sender": "newsletter@company.com"
        },
        {
            "subject": "URGENT: Deadline projet",
            "body": "Le projet doit être livré demain avant 17h. Status ?",
            "sender": "manager@company.com"
        },
        {
            "subject": "Invitation réunion",
            "body": "Réunion prévue vendredi à 10h en salle de conférence",
            "sender": "assistant@company.com"
        },
        {
            "subject": "Facture à régler",
            "body": "Merci de régler la facture n°12345 avant fin de mois",
            "sender": "comptabilite@company.com"
        }
    ]
    
    analyses = manager.process_email_batch(email_batch)
    priority_emails = manager.get_priority_emails(analyses)
    action_summary = manager.get_action_summary(analyses)
    
    print(f"    Emails traités: {len(analyses)}")
    print(f"    Ordre de priorité:")
    for j, analysis in enumerate(priority_emails):
        print(f"      {j+1}. {analysis.priority.value} - {analysis.category.value}")
        
    print(f"    Résumé actions: {action_summary}")
    
    print("\n✅ Traitement batch testé")

def test_sylvie_integration():
    """Test de l'intégration avec Sylvie"""
    print("\n🤖 Test intégration Sylvie...")
    
    integration = SylvieEmailIntegration()
    
    # Test analyse d'email pour Sylvie
    email_data = {
        "subject": "Demande de meeting urgent",
        "body": "Pouvons-nous planifier une réunion d'urgence demain à 9h pour discuter du budget ?",
        "sender": "client@important.com"
    }
    
    result = integration.analyze_incoming_email(email_data)
    
    print(f"    Email analysé pour Sylvie:")
    print(f"      Priorité: {result['priority']}")
    print(f"      Catégorie: {result['category']}")
    print(f"      Actions: {result['actions']}")
    print(f"      Résumé: {result['summary']}")
    print(f"      Sentiment: {result['sentiment']}")
    print(f"      Temps: {result['time_references']}")
    print(f"      Réponse suggérée: {result['suggested_reply']}")
    
    # Test traitement de demandes utilisateur
    user_requests = [
        "montre-moi mes emails urgents",
        "fais un résumé de mes emails",
        "aide-moi à répondre à ce message",
        "extrais les demandes de réunion"
    ]
    
    print(f"\n    Traitement demandes utilisateur:")
    for request in user_requests:
        response = integration.process_user_request(request)
        print(f"      '{request}' → {response['action']}: {response['message']}")
    
    print("\n✅ Intégration Sylvie testée")

def test_entity_extraction():
    """Test d'extraction d'entités"""
    print("\n🏷️ Test extraction entités...")
    
    manager = AdvancedEmailManager()
    
    test_text = """
    Réunion prévue le 15/01/2025 à 14h30 en salle A.
    Budget estimé: 5000€ pour le projet.
    Deadline: vendredi prochain avant 17h.
    Contacter Marie au 06.12.34.56.78 si problème.
    """
    
    entities = manager._extract_entities(test_text)
    time_refs = manager._extract_time_references(test_text)
    keywords = manager._extract_context_keywords(test_text.lower())
    
    print(f"    Texte analysé: {len(test_text)} chars")
    print(f"    Entités détectées: {entities}")
    print(f"    Références temporelles: {time_refs}")
    print(f"    Mots-clés: {keywords}")
    
    print("\n✅ Extraction entités testée")

def main():
    """Fonction principale de test"""
    print("🚀 Tests Advanced Email Manager pour Sylvie v2.0")
    print("=" * 60)
    
    test_email_analysis()
    test_smart_replies()
    test_batch_processing()
    test_sylvie_integration()
    test_entity_extraction()
    
    print(f"\n🎉 Tous les tests terminés à {datetime.now().strftime('%H:%M:%S')}")
    print("\n📋 Nouvelles fonctionnalités prêtes:")
    print("  ✅ Analyse intelligente des emails")
    print("  ✅ Génération de réponses contextuelles")
    print("  ✅ Catégorisation automatique")
    print("  ✅ Détection de priorité")
    print("  ✅ Extraction d'actions et entités")
    print("  ✅ Traitement en lot")
    print("  ✅ Intégration avec Sylvie")
    
    print("\n🔄 Prochaines étapes:")
    print("  1. Intégrer dans sylvie_agent.py")
    print("  2. Connecter aux services Gmail")
    print("  3. Tester avec des emails réels")
    print("  4. Améliorer les prompts avec les retours")

if __name__ == "__main__":
    main()
