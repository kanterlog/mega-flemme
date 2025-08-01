"""
📅 Service Calendar pour Sylvie
Phase 3.1 - Intégration Google Calendar

Gestion complète du calendrier Google pour KanterMator
"""

import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class CalendarService:
    """Service de gestion du calendrier Google"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.calendar_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Calendar est initialisé"""
        if self.calendar_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.calendar_service = build('calendar', 'v3', credentials=credentials)
                logger.info("✅ Service Calendar initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Calendar", error=str(e))
                raise
    
    async def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les événements à venir
        
        Args:
            max_results: Nombre maximum d'événements à récupérer
            
        Returns:
            Liste des événements à venir
        """
        await self._ensure_service_initialized()
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            parsed_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                parsed_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'Sans titre'),
                    'start': start,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'attendees': len(event.get('attendees', [])),
                    'link': event.get('htmlLink', '')
                })
            
            logger.info("📅 Événements récupérés", count=len(parsed_events))
            return parsed_events
            
        except HttpError as e:
            logger.error("❌ Erreur API Calendar", error=str(e))
            return []
        except Exception as e:
            logger.error("❌ Erreur inattendue Calendar", error=str(e))
            return []
    
    async def get_events_for_date(self, date_str: str) -> List[Dict[str, Any]]:
        """Récupère les événements pour une date donnée"""
        await self._ensure_service_initialized()
        
        try:
            # Parse de la date
            target_date = datetime.fromisoformat(date_str.replace('Z', ''))
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            parsed_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                parsed_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'Sans titre'),
                    'start': start,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'attendees': len(event.get('attendees', [])),
                    'link': event.get('htmlLink', '')
                })
            
            return parsed_events
            
        except Exception as e:
            logger.error("❌ Erreur récupération événements date", error=str(e))
            return []
    
    async def create_event(self, title: str, start_time: str, duration: int = 60) -> Optional[Dict[str, Any]]:
        """Crée un nouvel événement"""
        await self._ensure_service_initialized()
        
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', ''))
            end_dt = start_dt + timedelta(minutes=duration)
            
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
            }
            
            created_event = self.calendar_service.events().insert(
                calendarId='primary', 
                body=event
            ).execute()
            
            logger.info("✅ Événement créé", title=title)
            return {
                'id': created_event['id'],
                'title': created_event.get('summary'),
                'start': created_event['start'].get('dateTime'),
                'link': created_event.get('htmlLink')
            }
            
        except Exception as e:
            logger.error("❌ Erreur création événement", error=str(e))
            return None
    
    async def check_conflicts(self, date_str: str) -> List[Dict[str, Any]]:
        """Vérifie les conflits d'horaires pour une date"""
        events = await self.get_events_for_date(date_str)
        
        conflicts = []
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                # Logic simple de détection de conflit
                if self._events_overlap(event1, event2):
                    conflicts.append({
                        'event1': event1,
                        'event2': event2,
                        'type': 'overlap'
                    })
        
        return conflicts
    
    def _events_overlap(self, event1: Dict, event2: Dict) -> bool:
        """Vérifie si deux événements se chevauchent"""
        try:
            start1 = datetime.fromisoformat(event1['start'].replace('Z', ''))
            start2 = datetime.fromisoformat(event2['start'].replace('Z', ''))
            # Logique simplifiée - en réalité il faudrait les heures de fin
            return abs((start1 - start2).total_seconds()) < 3600  # 1 heure
        except:
            return False

# Instance globale du service
calendar_service = CalendarService()
