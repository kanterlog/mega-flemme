"""
📧 Service Gmail pour Sylvie
Phase 3.7 - Intégration Gmail

Sylvie peut lire, analyser et envoyer des emails
pour une assistance complète
"""

import base64
import email
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import structlog
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

from app.services.google_auth import GoogleAuthService

logger = structlog.get_logger(__name__)

class GmailService:
    """Service Gmail pour l'agent Sylvie"""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.gmail_service = None
        # Pas d'initialisation synchrone, sera fait lors du premier appel async
    
    async def _ensure_service_initialized(self):
        """Assure que le service Gmail est initialisé"""
        if self.gmail_service is None:
            try:
                credentials = await self.auth_service.get_credentials()
                self.gmail_service = build('gmail', 'v1', credentials=credentials)
                logger.info("✅ Service Gmail initialisé")
            except Exception as e:
                logger.error("❌ Erreur initialisation Gmail", error=str(e))
                raise
    
    async def get_recent_emails(self, max_results: int = 10, query: str = None) -> List[Dict[str, Any]]:
        """
        Récupère les emails récents
        
        Args:
            max_results: Nombre maximum d'emails à récupérer
            query: Requête de filtrage optionnelle
            
        Returns:
            Liste des emails récents avec métadonnées
        """
        await self._ensure_service_initialized()
        try:
            # Recherche par défaut : emails non lus des 7 derniers jours
            if not query:
                query = "is:unread newer_than:7d"
            
            # Recherche des messages
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = await self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"📧 {len(emails)} emails récupérés", query=query)
            return emails
            
        except HttpError as e:
            logger.error("❌ Erreur récupération emails", error=str(e))
            return []
    
    async def _get_email_details(self, message_id: str) -> Dict[str, Any]:
        """Récupération des détails d'un email"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Extraction des headers
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            # Extraction du contenu
            body = self._extract_email_body(message['payload'])
            
            return {
                'id': message_id,
                'thread_id': message['threadId'],
                'subject': headers.get('Subject', 'Sans sujet'),
                'sender': headers.get('From', 'Inconnu'),
                'date': headers.get('Date', ''),
                'body': body,
                'is_unread': 'UNREAD' in message.get('labelIds', []),
                'is_important': 'IMPORTANT' in message.get('labelIds', []),
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur détails email {message_id}", error=str(e))
            return None
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extraction du corps de l'email"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        elif payload['mimeType'] == 'text/plain':
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    async def search_emails(self, 
                          keywords: List[str] = None,
                          sender: str = None, 
                          date_from: datetime = None,
                          date_to: datetime = None,
                          max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Recherche avancée d'emails
        
        Args:
            keywords: Mots-clés à rechercher
            sender: Adresse email de l'expéditeur
            date_from: Date de début
            date_to: Date de fin
            max_results: Nombre max de résultats
        """
        
        # Construction de la requête Gmail
        query_parts = []
        
        if keywords:
            keywords_query = " OR ".join([f'"{kw}"' for kw in keywords])
            query_parts.append(f"({keywords_query})")
        
        if sender:
            query_parts.append(f"from:{sender}")
        
        if date_from:
            date_str = date_from.strftime("%Y/%m/%d")
            query_parts.append(f"after:{date_str}")
        
        if date_to:
            date_str = date_to.strftime("%Y/%m/%d")
            query_parts.append(f"before:{date_str}")
        
        query = " ".join(query_parts) if query_parts else "in:inbox"
        
        return await self.get_recent_emails(max_results, query)
    
    async def analyze_emails_for_sylvie(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse des emails pour l'assistant Sylvie
        
        Détecte :
        - Emails urgents ou importants
        - Demandes d'aide ou questions
        - Notifications système
        - Actions requises
        """
        
        analysis = {
            'total_emails': len(emails),
            'urgent_emails': [],
            'educational_content': [],
            'system_notifications': [],
            'action_required': [],
            'summary': {}
        }
        
        # Mots-clés pour classification
        urgent_keywords = ['urgent', 'asap', 'important', 'deadline', 'échéance']
        educational_keywords = ['élève', 'cours', 'progression', 'évaluation', 'classe']
        system_keywords = ['notification', 'alert', 'error', 'erreur', 'système']
        action_keywords = ['répondre', 'confirmer', 'valider', 'approuver', 'action']
        
        for email in emails:
            subject_lower = email['subject'].lower()
            body_lower = email['body'].lower()
            content = f"{subject_lower} {body_lower}"
            
            # Classification des emails
            if any(kw in content for kw in urgent_keywords):
                analysis['urgent_emails'].append({
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'date': email['date'],
                    'reason': 'Contient des mots-clés urgents'
                })
            
            if any(kw in content for kw in educational_keywords):
                analysis['educational_content'].append({
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'relevance': 'Contenu éducatif détecté'
                })
            
            if any(kw in content for kw in system_keywords):
                analysis['system_notifications'].append({
                    'subject': email['subject'],
                    'type': 'Notification système'
                })
            
            if any(kw in content for kw in action_keywords) or email['is_unread']:
                analysis['action_required'].append({
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'action': 'Lecture/Réponse requise'
                })
        
        # Résumé
        analysis['summary'] = {
            'urgent_count': len(analysis['urgent_emails']),
            'educational_count': len(analysis['educational_content']),
            'unread_count': sum(1 for e in emails if e['is_unread']),
            'action_required_count': len(analysis['action_required'])
        }
        
        return analysis
    
    async def send_email(self, 
                        to: str,
                        subject: str, 
                        body: str,
                        cc: List[str] = None,
                        bcc: List[str] = None) -> bool:
        """
        Envoi d'email via Sylvie
        
        Args:
            to: Destinataire principal
            subject: Sujet de l'email
            body: Corps du message
            cc: Destinataires en copie
            bcc: Destinataires en copie cachée
            
        Returns:
            True si envoyé avec succès
        """
        try:
            # Construction du message
            message = self._create_message(to, subject, body, cc, bcc)
            
            # Envoi
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            logger.info("📧 Email envoyé par Sylvie", 
                       to=to, 
                       subject=subject,
                       message_id=sent_message['id'])
            
            return True
            
        except Exception as e:
            logger.error("❌ Erreur envoi email", 
                        to=to, 
                        subject=subject, 
                        error=str(e))
            return False
    
    def _create_message(self, to: str, subject: str, body: str, cc: List[str] = None, bcc: List[str] = None) -> Dict:
        """Création du message email au format Gmail API"""
        
        message_text = f"To: {to}\n"
        
        if cc:
            message_text += f"Cc: {', '.join(cc)}\n"
        
        if bcc:
            message_text += f"Bcc: {', '.join(bcc)}\n"
        
        message_text += f"Subject: {subject}\n\n{body}"
        
        encoded_message = base64.urlsafe_b64encode(message_text.encode('utf-8')).decode('utf-8')
        
        return {'raw': encoded_message}
    
    async def get_gmail_summary_for_sylvie(self) -> Dict[str, Any]:
        """
        Résumé Gmail pour l'assistant Sylvie
        
        Returns:
            Informations utiles pour les réponses de Sylvie
        """
        try:
            # Emails récents non lus
            unread_emails = await self.get_recent_emails(5, "is:unread")
            
            # Analyse des emails
            email_analysis = await self.analyze_emails_for_sylvie(unread_emails)
            
            # Statistiques Gmail
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            
            return {
                'email_address': profile.get('emailAddress'),
                'total_messages': profile.get('messagesTotal', 0),
                'unread_analysis': email_analysis,
                'recent_unread': len(unread_emails),
                'urgent_items': email_analysis['summary']['urgent_count'],
                'action_required': email_analysis['summary']['action_required_count'],
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("❌ Erreur résumé Gmail", error=str(e))
            return {
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }

# Instance globale du service Gmail
gmail_service = GmailService()
