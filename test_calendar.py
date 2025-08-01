#!/usr/bin/env python3
"""
🧪 Test direct du service Calendar
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Ajout du chemin parent pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.calendar_service import CalendarService

async def test_calendar_service():
    """Test direct du service Calendar"""
    print("🧪 Test du service Calendar...")
    
    calendar_service = CalendarService()
    
    try:
        # Test 1: Récupérer les événements à venir
        print("\n📅 Test 1: Événements à venir")
        events = await calendar_service.get_upcoming_events(5)
        print(f"✅ {len(events)} événements trouvés")
        for event in events[:3]:
            print(f"  - {event.get('title', 'Sans titre')}: {event.get('start', 'N/A')}")
        
        # Test 2: Créer un événement test
        print("\n📅 Test 2: Création d'événement")
        future_time = datetime.now() + timedelta(hours=1)
        start_time = future_time.isoformat()
        
        created_event = await calendar_service.create_event(
            title="Test Sylvie - Événement automatique",
            start_time=start_time,
            duration=30
        )
        
        if created_event:
            print(f"✅ Événement créé: {created_event['title']}")
            print(f"  ID: {created_event['id']}")
            print(f"  Début: {created_event['start']}")
            print(f"  Lien: {created_event.get('link', 'N/A')}")
        else:
            print("❌ Échec création événement")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test calendar: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_calendar_service())
    if result:
        print("\n🎉 Service Calendar opérationnel !")
    else:
        print("\n⚠️  Problème avec le service Calendar.")
