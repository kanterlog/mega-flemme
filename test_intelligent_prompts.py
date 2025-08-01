#!/usr/bin/env python3
"""
🧪 Tests complets des prompts intelligents de Sylvie
Version 2.0 - Validation de la compréhension flexible
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.intelligent_prompts import IntelligentPrompts

def test_time_extraction():
    """Test de l'extraction des références temporelles"""
    print("🕐 Test extraction temps...")
    
    test_cases = [
        "rdv demain 14h",
        "réunion vendredi matin",
        "appel cet après-midi", 
        "événement lundi à 16h30",
        "meeting demain midi",
        "présentation après-demain 9h"
    ]
    
    for text in test_cases:
        time_info = IntelligentPrompts.extract_time_references(text)
        print(f"  '{text}' → {time_info}")
    
    print("✅ Extraction temps testée\n")

def test_prompt_generation():
    """Test de génération de prompts"""
    print("📝 Test génération prompts...")
    
    # Test prompt d'intention
    message = "crée un rdv demain 14h avec Pierre"
    intent_prompt = IntelligentPrompts.get_intent_analysis_prompt(message, "conversation précédente")
    print(f"Prompt d'intention généré (longueur: {len(intent_prompt)} chars)")
    
    # Test prompt de réponse
    response_prompt = IntelligentPrompts.get_response_generation_prompt(
        message="check mes mails",
        intent="check_emails", 
        action_taken="Vérification emails",
        action_result={"count": 5, "unread": 2}
    )
    print(f"Prompt de réponse généré (longueur: {len(response_prompt)} chars)")
    
    # Test prompt d'erreur
    error_prompt = IntelligentPrompts.get_error_handling_prompt(
        "permission_denied",
        "Accès Gmail refusé"
    )
    print(f"Prompt d'erreur généré (longueur: {len(error_prompt)} chars)")
    
    print("✅ Génération prompts testée\n")

def simulate_conversations():
    """Simulation de conversations flexibles"""
    print("💬 Simulation conversations flexibles...")
    
    flexible_messages = [
        # Calendrier
        "crée un rdv demain 14h",
        "planifie une réunion équipe vendredi",
        "ajoute un event lundi matin",
        "rdv dentiste après-demain 16h30",
        
        # Emails  
        "check mes mails",
        "regarde si j'ai reçu quelque chose",
        "vérifie ma boîte mail",
        "envoie un mail à Pierre",
        
        # Tâches
        "ajoute une tâche",
        "note que je dois appeler Marie",
        "crée une todo: acheter du pain",
        "mes tâches du jour",
        
        # Drive
        "mes fichiers récents",
        "cherche le document budget",
        "organise mon drive",
        "montre mes photos"
    ]
    
    for msg in flexible_messages:
        time_info = IntelligentPrompts.extract_time_references(msg)
        time_str = f" [temps: {time_info}]" if time_info else ""
        print(f"  '{msg}'{time_str}")
    
    print("✅ Conversations simulées\n")

def test_system_prompt():
    """Test du prompt système"""
    print("🤖 Test prompt système...")
    
    system_prompt = IntelligentPrompts.get_system_prompt()
    print(f"Prompt système: {len(system_prompt)} caractères")
    
    # Vérifications
    checks = [
        ("personnalisation", "mon assistante" in system_prompt.lower()),
        ("google workspace", "google workspace" in system_prompt.lower()),
        ("naturel", "naturel" in system_prompt.lower()),
        ("tutoiement", "tu es" in system_prompt.lower()),
        ("efficacité", "efficace" in system_prompt.lower())
    ]
    
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"  {status} {check_name}")
    
    print("✅ Prompt système testé\n")

async def main():
    """Test principal"""
    print("🚀 Tests des Prompts Intelligents Sylvie v2.0")
    print("=" * 50)
    
    test_time_extraction()
    test_prompt_generation()  
    simulate_conversations()
    test_system_prompt()
    
    print("🎉 Tous les tests des prompts intelligents terminés !")
    print("\n📋 Prêt pour tester avec Sylvie:")
    print("  - 'rdv demain 14h avec Pierre'")
    print("  - 'check mes mails'") 
    print("  - 'ajoute une tâche: appeler Marie'")
    print("  - 'mes fichiers récents'")

if __name__ == "__main__":
    asyncio.run(main())
