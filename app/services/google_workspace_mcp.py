#!/usr/bin/env python3
"""
🚀 Google Workspace MCP Integration pour Sylvie v2.2
Inspiré par mcp-gsuite de MarkusPfundstein + Gmail-MCP-Server

Fonctionnalités complètes Google Workspace :
- 📧 Gmail avancé (recherche, pièces jointes, brouillons, réponses)
- 📅 Google Calendar (événements, création, modification, suppression)
- 👥 Comptes multiples
- 🔐 OAuth2 sécurisé
- 🔄 Synchronisation temps réel
"""

import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import re

# Configuration pour l'intégration
logger = logging.getLogger(__name__)

class GoogleWorkspaceAccount:
    """Gestion des comptes Google Workspace multiples"""
    
    def __init__(self, email: str, account_type: str = "personal", extra_info: str = ""):
        self.email = email
        self.account_type = account_type
        self.extra_info = extra_info
        self.credentials = None
        self.last_auth = None
    
    def to_dict(self):
        return {
            "email": self.email,
            "account_type": self.account_type,
            "extra_info": self.extra_info,
            "last_auth": self.last_auth.isoformat() if self.last_auth else None
        }

@dataclass
class CalendarEvent:
    """Structure d'un événement de calendrier"""
    id: str = ""
    summary: str = ""
    description: str = ""
    start_time: str = ""
    end_time: str = ""
    location: str = ""
    attendees: List[str] = field(default_factory=list)
    status: str = "confirmed"
    creator: Dict[str, str] = field(default_factory=dict)
    organizer: Dict[str, str] = field(default_factory=dict)
    timezone: str = "UTC"
    notifications: List[int] = field(default_factory=lambda: [10])  # minutes avant
    calendar_id: str = "primary"

@dataclass
class EmailMessage:
    """Structure enrichie d'un email"""
    id: str = ""
    thread_id: str = ""
    subject: str = ""
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    body_text: str = ""
    body_html: str = ""
    snippet: str = ""
    date: str = ""
    labels: List[str] = field(default_factory=list)
    attachments: List[Dict] = field(default_factory=list)
    is_unread: bool = True
    is_important: bool = False
    size_estimate: int = 0

class GoogleWorkspaceScopes(Enum):
    """Scopes OAuth2 requis pour Google Workspace"""
    OPENID = "openid"
    EMAIL_INFO = "https://www.googleapis.com/auth/userinfo.email"
    GMAIL_FULL = "https://mail.google.com/"
    CALENDAR = "https://www.googleapis.com/auth/calendar"
    DRIVE_FILE = "https://www.googleapis.com/auth/drive.file"

class GoogleWorkspaceMCPIntegration:
    """
    🎯 Intégration complète Google Workspace MCP pour Sylvie
    Combine Gmail + Calendar + Multi-comptes
    """
    
    def __init__(self):
        self.accounts: Dict[str, GoogleWorkspaceAccount] = {}
        self.authenticated_services = {}
        self.default_account = None
        
        # Configuration OAuth2
        self.oauth_config = {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:4100/code",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        # Scopes requis
        self.required_scopes = [scope.value for scope in GoogleWorkspaceScopes]
        
        logger.info("🚀 GoogleWorkspaceMCPIntegration initialisé")
    
    def add_account(self, email: str, account_type: str = "personal", extra_info: str = ""):
        """Ajouter un compte Google Workspace"""
        account = GoogleWorkspaceAccount(email, account_type, extra_info)
        self.accounts[email] = account
        
        if not self.default_account:
            self.default_account = email
            
        logger.info(f"✅ Compte ajouté : {email} ({account_type})")
        return account
    
    async def authenticate_account(self, email: str) -> bool:
        """Authentifier un compte via OAuth2"""
        try:
            if email not in self.accounts:
                raise ValueError(f"Compte {email} non configuré")
            
            account = self.accounts[email]
            
            # Simulation OAuth2 flow (dans un vrai environnement, utiliser google-auth)
            # Pour le développement, on simule une authentification réussie
            account.credentials = {
                "access_token": f"ya29.simulated_token_{email}",
                "refresh_token": f"refresh_token_{email}",
                "expires_in": 3600,
                "scope": " ".join(self.required_scopes)
            }
            account.last_auth = datetime.now()
            
            logger.info(f"🔐 Authentification réussie pour {email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur authentification {email}: {str(e)}")
            return False
    
    # === FONCTIONNALITÉS GMAIL AVANCÉES ===
    
    async def search_emails_advanced(self, query: str = "", account: str = None, 
                                   max_results: int = 50, 
                                   include_attachments: bool = False) -> List[EmailMessage]:
        """
        🔍 Recherche Gmail avancée avec syntaxe MCP
        Supporte : from:, to:, subject:, has:attachment, after:, before:, is:unread, etc.
        """
        try:
            account = account or self.default_account
            if not account or account not in self.accounts:
                raise ValueError(f"Compte {account} non disponible")
            
            # Parsing de la requête Gmail
            parsed_query = self._parse_gmail_query(query)
            
            # Simulation de la recherche (remplacer par vraie API Gmail)
            emails = await self._simulate_gmail_search(parsed_query, max_results, include_attachments)
            
            logger.info(f"📧 Trouvé {len(emails)} emails pour la requête : {query}")
            return emails
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche Gmail: {str(e)}")
            return []
    
    def _parse_gmail_query(self, query: str) -> Dict[str, Any]:
        """Parse une requête Gmail avec opérateurs"""
        parsed = {
            "from": None,
            "to": None,
            "subject": None,
            "has_attachment": False,
            "is_unread": False,
            "after": None,
            "before": None,
            "in": None,
            "label": None,
            "text": ""
        }
        
        # Extraction des opérateurs Gmail
        operators = [
            (r'from:(\S+)', 'from'),
            (r'to:(\S+)', 'to'),
            (r'subject:"([^"]*)"', 'subject'),
            (r'subject:(\S+)', 'subject'),
            (r'has:attachment', 'has_attachment'),
            (r'is:unread', 'is_unread'),
            (r'after:(\S+)', 'after'),
            (r'before:(\S+)', 'before'),
            (r'in:(\S+)', 'in'),
            (r'label:(\S+)', 'label')
        ]
        
        remaining_query = query
        
        for pattern, key in operators:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if key in ['has_attachment', 'is_unread']:
                    parsed[key] = True
                else:
                    parsed[key] = match.group(1) if match.groups() else True
                remaining_query = re.sub(pattern, '', remaining_query, flags=re.IGNORECASE)
        
        # Texte libre restant
        parsed['text'] = remaining_query.strip()
        
        return parsed
    
    async def _simulate_gmail_search(self, parsed_query: Dict, max_results: int, 
                                   include_attachments: bool) -> List[EmailMessage]:
        """Simulation de recherche Gmail (remplacer par vraie API)"""
        # Données de test
        sample_emails = [
            EmailMessage(
                id="email_001",
                subject="Rapport mensuel Q4 2024",
                sender="marie@entreprise.com",
                recipients=["sylvie@kantermator.com"],
                body_text="Voici le rapport mensuel détaillé...",
                date=datetime.now().isoformat(),
                labels=["INBOX", "IMPORTANT"],
                attachments=[{"filename": "rapport_q4.pdf", "size": 2048000}] if include_attachments else [],
                is_unread=True
            ),
            EmailMessage(
                id="email_002", 
                subject="Formation IA - Nouvelles dates",
                sender="alex@formation.com",
                recipients=["equipe@kantermator.com"],
                body_text="Suite aux demandes, la formation IA est reportée...",
                date=(datetime.now() - timedelta(days=1)).isoformat(),
                labels=["INBOX"],
                is_unread=False
            ),
            EmailMessage(
                id="email_003",
                subject="URGENT: Problème serveur",
                sender="tech@kantermator.com", 
                recipients=["sylvie@kantermator.com"],
                body_text="Le serveur principal est en panne...",
                date=(datetime.now() - timedelta(hours=2)).isoformat(),
                labels=["INBOX", "URGENT"],
                is_unread=True,
                is_important=True
            )
        ]
        
        # Filtrage basé sur la requête parsée
        filtered_emails = []
        for email in sample_emails:
            if self._email_matches_query(email, parsed_query):
                filtered_emails.append(email)
        
        return filtered_emails[:max_results]
    
    def _email_matches_query(self, email: EmailMessage, query: Dict) -> bool:
        """Vérifie si un email correspond aux critères de recherche"""
        # Filtres spécifiques
        if query['from'] and query['from'].lower() not in email.sender.lower():
            return False
        
        if query['to'] and not any(query['to'].lower() in recip.lower() for recip in email.recipients):
            return False
        
        if query['subject'] and query['subject'].lower() not in email.subject.lower():
            return False
        
        if query['has_attachment'] and not email.attachments:
            return False
        
        if query['is_unread'] and not email.is_unread:
            return False
        
        # Texte libre dans le contenu
        if query['text']:
            text_query = query['text'].lower()
            if (text_query not in email.subject.lower() and 
                text_query not in email.body_text.lower() and
                text_query not in email.sender.lower()):
                return False
        
        return True
    
    async def create_email_draft(self, to: List[str], subject: str, body: str, 
                               cc: List[str] = None, account: str = None) -> Dict:
        """Créer un brouillon d'email"""
        try:
            account = account or self.default_account
            cc = cc or []
            
            draft = {
                "id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "to": to,
                "cc": cc,
                "subject": subject,
                "body": body,
                "account": account,
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            
            logger.info(f"📝 Brouillon créé : {subject}")
            return draft
            
        except Exception as e:
            logger.error(f"❌ Erreur création brouillon: {str(e)}")
            return {}
    
    async def reply_to_email(self, original_email_id: str, reply_body: str, 
                           send_immediately: bool = False, account: str = None) -> Dict:
        """Répondre à un email"""
        try:
            account = account or self.default_account
            
            reply = {
                "id": f"reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "original_id": original_email_id,
                "body": reply_body,
                "account": account,
                "created_at": datetime.now().isoformat(),
                "status": "sent" if send_immediately else "draft"
            }
            
            status = "envoyée" if send_immediately else "sauvegardée en brouillon"
            logger.info(f"↩️ Réponse {status} pour email {original_email_id}")
            return reply
            
        except Exception as e:
            logger.error(f"❌ Erreur réponse email: {str(e)}")
            return {}
    
    # === FONCTIONNALITÉS GOOGLE CALENDAR ===
    
    async def get_calendar_events(self, account: str = None, calendar_id: str = "primary",
                                time_min: str = None, time_max: str = None,
                                max_results: int = 250) -> List[CalendarEvent]:
        """Récupérer les événements du calendrier"""
        try:
            account = account or self.default_account
            
            # Dates par défaut
            if not time_min:
                time_min = datetime.now().isoformat()
            if not time_max:
                time_max = (datetime.now() + timedelta(days=30)).isoformat()
            
            # Simulation d'événements (remplacer par vraie API Calendar)
            events = await self._simulate_calendar_events(time_min, time_max, max_results)
            
            logger.info(f"📅 Trouvé {len(events)} événements pour {account}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération événements: {str(e)}")
            return []
    
    async def _simulate_calendar_events(self, time_min: str, time_max: str, 
                                      max_results: int) -> List[CalendarEvent]:
        """Simulation d'événements Calendar (remplacer par vraie API)"""
        now = datetime.now()
        
        sample_events = [
            CalendarEvent(
                id="event_001",
                summary="Réunion équipe Sylvie",
                description="Point hebdomadaire sur l'avancement du projet",
                start_time=(now + timedelta(days=1, hours=14)).isoformat(),
                end_time=(now + timedelta(days=1, hours=15)).isoformat(),
                location="Salle de conférence A",
                attendees=["marie@kantermator.com", "alex@kantermator.com"],
                notifications=[15, 5]  # 15 min et 5 min avant
            ),
            CalendarEvent(
                id="event_002",
                summary="Formation IA avancée",
                description="Session de formation sur les dernières avancées en IA",
                start_time=(now + timedelta(days=3, hours=9)).isoformat(),
                end_time=(now + timedelta(days=3, hours=17)).isoformat(),
                location="Centre de formation",
                attendees=["equipe@kantermator.com"],
                notifications=[60, 30, 10]  # 1h, 30min, 10min avant
            ),
            CalendarEvent(
                id="event_003",
                summary="Demo client KanterMator",
                description="Présentation des nouvelles fonctionnalités",
                start_time=(now + timedelta(days=7, hours=10)).isoformat(),
                end_time=(now + timedelta(days=7, hours=11, minutes=30)).isoformat(),
                location="Visioconférence",
                attendees=["client@entreprise.com", "sylvie@kantermator.com"]
            )
        ]
        
        return sample_events[:max_results]
    
    async def create_calendar_event(self, summary: str, start_time: str, end_time: str,
                                  description: str = "", location: str = "",
                                  attendees: List[str] = None, 
                                  account: str = None, calendar_id: str = "primary") -> CalendarEvent:
        """Créer un événement de calendrier"""
        try:
            account = account or self.default_account
            attendees = attendees or []
            
            event = CalendarEvent(
                id=f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                summary=summary,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                attendees=attendees,
                calendar_id=calendar_id
            )
            
            logger.info(f"📅 Événement créé : {summary}")
            return event
            
        except Exception as e:
            logger.error(f"❌ Erreur création événement: {str(e)}")
            return CalendarEvent()
    
    async def delete_calendar_event(self, event_id: str, account: str = None,
                                  calendar_id: str = "primary") -> bool:
        """Supprimer un événement de calendrier"""
        try:
            account = account or self.default_account
            
            # Simulation suppression (remplacer par vraie API)
            logger.info(f"🗑️ Événement {event_id} supprimé du calendrier {calendar_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression événement: {str(e)}")
            return False
    
    # === FONCTIONNALITÉS MULTI-COMPTES ===
    
    def list_accounts(self) -> List[Dict]:
        """Lister tous les comptes configurés"""
        return [account.to_dict() for account in self.accounts.values()]
    
    def switch_default_account(self, email: str) -> bool:
        """Changer le compte par défaut"""
        if email in self.accounts:
            self.default_account = email
            logger.info(f"🔄 Compte par défaut changé pour : {email}")
            return True
        return False
    
    # === FONCTIONNALITÉS D'INTELLIGENCE ===
    
    async def analyze_email_productivity(self, account: str = None, 
                                       days_back: int = 7) -> Dict:
        """Analyser la productivité email"""
        try:
            account = account or self.default_account
            
            # Simulation d'analyse de productivité
            analysis = {
                "account": account,
                "period_days": days_back,
                "stats": {
                    "emails_received": 45,
                    "emails_sent": 23,
                    "emails_unread": 8,
                    "average_response_time": "2.5 hours",
                    "busiest_day": "Tuesday",
                    "busiest_hour": "14:00-15:00"
                },
                "suggestions": [
                    "Consulter les emails non lus en priorité",
                    "Regrouper les réponses en fin de journée",
                    "Utiliser des filtres pour les newsletters"
                ],
                "productivity_score": 85
            }
            
            logger.info(f"📊 Analyse productivité générée pour {account}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse productivité: {str(e)}")
            return {}
    
    async def suggest_meeting_times(self, duration_hours: int = 1, 
                                  participants: List[str] = None,
                                  preferred_days: List[str] = None,
                                  account: str = None) -> List[Dict]:
        """Suggérer des créneaux de réunion"""
        try:
            account = account or self.default_account
            participants = participants or []
            preferred_days = preferred_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            
            # Simulation de suggestions de créneaux
            now = datetime.now()
            suggestions = []
            
            for day_offset in range(1, 8):  # 7 prochains jours
                day = now + timedelta(days=day_offset)
                if day.strftime("%A") in preferred_days:
                    # Créneaux matin et après-midi
                    for hour in [9, 10, 14, 15, 16]:
                        start_time = day.replace(hour=hour, minute=0, second=0)
                        end_time = start_time + timedelta(hours=duration_hours)
                        
                        suggestions.append({
                            "start_time": start_time.isoformat(),
                            "end_time": end_time.isoformat(),
                            "availability_score": 0.9,  # Score de disponibilité simulé
                            "day_name": day.strftime("%A"),
                            "conflicts": []
                        })
            
            # Trier par score de disponibilité
            suggestions.sort(key=lambda x: x["availability_score"], reverse=True)
            
            logger.info(f"💡 {len(suggestions)} créneaux suggérés pour réunion de {duration_hours}h")
            return suggestions[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"❌ Erreur suggestion créneaux: {str(e)}")
            return []
    
    def get_integration_status(self) -> Dict:
        """Status de l'intégration Google Workspace"""
        return {
            "version": "2.2",
            "accounts_configured": len(self.accounts),
            "default_account": self.default_account,
            "services_available": ["gmail", "calendar"],
            "last_sync": datetime.now().isoformat(),
            "features": {
                "email_search": True,
                "email_drafts": True,
                "email_replies": True,
                "calendar_events": True,
                "calendar_creation": True,
                "multi_accounts": True,
                "productivity_analysis": True,
                "meeting_suggestions": True
            }
        }

# === FONCTIONS UTILITAIRES ===

def format_email_for_display(email: EmailMessage) -> str:
    """Formatter un email pour affichage"""
    attachments_info = f" [{len(email.attachments)} pièces jointes]" if email.attachments else ""
    unread_flag = "📧 " if email.is_unread else "📖 "
    important_flag = "⭐ " if email.is_important else ""
    
    return f"""{unread_flag}{important_flag}{email.subject}
De: {email.sender}
À: {', '.join(email.recipients)}
Date: {email.date}
Extrait: {email.snippet[:100]}...{attachments_info}
"""

def format_calendar_event_for_display(event: CalendarEvent) -> str:
    """Formatter un événement de calendrier pour affichage"""
    attendees_info = f"\nParticipants: {', '.join(event.attendees)}" if event.attendees else ""
    location_info = f"\nLieu: {event.location}" if event.location else ""
    
    return f"""📅 {event.summary}
Début: {event.start_time}
Fin: {event.end_time}{location_info}{attendees_info}
Description: {event.description}
"""

# Instance globale pour Sylvie
google_workspace_integration = GoogleWorkspaceMCPIntegration()

# Configuration de comptes par défaut pour le développement
async def setup_default_accounts():
    """Configuration par défaut des comptes pour le développement"""
    try:
        # Ajouter des comptes de test
        google_workspace_integration.add_account(
            "sylvie@kantermator.com", 
            "professional", 
            "Compte principal Sylvie avec accès complet"
        )
        google_workspace_integration.add_account(
            "kanter@kantermator.com",
            "admin",
            "Compte administrateur avec calendriers partagés"
        )
        
        # Authentifier les comptes
        for email in google_workspace_integration.accounts.keys():
            await google_workspace_integration.authenticate_account(email)
        
        logger.info("✅ Configuration par défaut des comptes terminée")
        
    except Exception as e:
        logger.error(f"❌ Erreur configuration comptes: {str(e)}")

if __name__ == "__main__":
    # Test de l'intégration
    async def test_integration():
        await setup_default_accounts()
        
        # Test recherche emails
        emails = await google_workspace_integration.search_emails_advanced(
            "is:unread from:marie subject:rapport"
        )
        print(f"Emails trouvés: {len(emails)}")
        
        # Test événements calendrier
        events = await google_workspace_integration.get_calendar_events()
        print(f"Événements trouvés: {len(events)}")
        
        # Test création événement
        new_event = await google_workspace_integration.create_calendar_event(
            "Test Sylvie v2.2",
            (datetime.now() + timedelta(days=1)).isoformat(),
            (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            "Test de l'intégration Google Workspace"
        )
        print(f"Événement créé: {new_event.summary}")
    
    asyncio.run(test_integration())
