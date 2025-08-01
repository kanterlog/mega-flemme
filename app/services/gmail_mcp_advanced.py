#!/usr/bin/env python3
"""
🔥 Advanced Gmail MCP Integration pour Sylvie v2.1
Inspiré par Gmail-MCP-Server : https://github.com/GongRzhe/Gmail-MCP-Server

Nouvelles fonctionnalités avancées :
- Gestion complète des pièces jointes
- Opérations par lot (batch operations)
- Gestion avancée des labels Gmail
- Recherche Gmail avec syntaxe avancée
- Extraction MIME intelligente
- Support multilingue complet
"""

import asyncio
import base64
import os
import mimetypes
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailSearchOperator(Enum):
    """Opérateurs de recherche Gmail avancés"""
    FROM = "from:"
    TO = "to:"
    SUBJECT = "subject:"
    HAS_ATTACHMENT = "has:attachment"
    AFTER = "after:"
    BEFORE = "before:"
    IS_UNREAD = "is:unread"
    IS_READ = "is:read"
    IS_IMPORTANT = "is:important"
    LABEL = "label:"
    LARGER = "larger:"
    SMALLER = "smaller:"
    CATEGORY = "category:"

class EmailMimeType(Enum):
    """Types MIME pour les emails"""
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"
    MULTIPART_ALTERNATIVE = "multipart/alternative"
    MULTIPART_MIXED = "multipart/mixed"

@dataclass
class EmailAttachment:
    """Représentation d'une pièce jointe email"""
    id: str
    filename: str
    mime_type: str
    size: int
    download_id: Optional[str] = None
    content_data: Optional[bytes] = None

@dataclass
class EmailContent:
    """Contenu extrait d'un email"""
    plain_text: str = ""
    html_content: str = ""
    attachments: List[EmailAttachment] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class BatchOperation:
    """Opération par lot sur les emails"""
    message_ids: List[str]
    operation_type: str
    batch_size: int = 50
    add_labels: List[str] = field(default_factory=list)
    remove_labels: List[str] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    errors: List[str] = field(default_factory=list)

class AdvancedGmailManager:
    """
    Gestionnaire Gmail avancé inspiré du projet Gmail-MCP-Server
    Fonctionnalités complètes pour la gestion Gmail avec IA
    """
    
    def __init__(self, gmail_service):
        self.gmail = gmail_service
        self.user_id = 'me'
        
    async def search_emails_advanced(self, 
                                   query: str, 
                                   max_results: int = 10,
                                   include_spam_trash: bool = False) -> List[Dict[str, Any]]:
        """
        Recherche avancée d'emails avec syntaxe Gmail complète
        
        Args:
            query: Requête Gmail (ex: "from:john@example.com after:2024/01/01 has:attachment")
            max_results: Nombre maximum de résultats
            include_spam_trash: Inclure spam et corbeille
            
        Returns:
            Liste des emails trouvés avec métadonnées complètes
        """
        try:
            results = self.gmail.users().messages().list(
                userId=self.user_id,
                q=query,
                maxResults=max_results,
                includeSpamTrash=include_spam_trash
            ).execute()
            
            messages = results.get('messages', [])
            
            # Récupération des détails pour chaque message
            detailed_messages = []
            for msg in messages:
                try:
                    detail = await self._get_message_details(msg['id'])
                    detailed_messages.append(detail)
                except Exception as e:
                    print(f"Erreur lors de la récupération du message {msg['id']}: {e}")
                    
            return detailed_messages
            
        except HttpError as error:
            print(f"Erreur API Gmail lors de la recherche: {error}")
            return []
            
    async def _get_message_details(self, message_id: str) -> Dict[str, Any]:
        """Récupère les détails complets d'un message"""
        try:
            message = self.gmail.users().messages().get(
                userId=self.user_id, 
                id=message_id,
                format='full'
            ).execute()
            
            # Extraction des headers
            headers = {}
            payload = message.get('payload', {})
            if 'headers' in payload:
                headers = {h['name']: h['value'] for h in payload['headers']}
            
            # Extraction du contenu et pièces jointes
            content = await self._extract_email_content(payload)
            
            return {
                'id': message_id,
                'thread_id': message.get('threadId', ''),
                'snippet': message.get('snippet', ''),
                'headers': headers,
                'subject': headers.get('Subject', ''),
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'date': headers.get('Date', ''),
                'labels': message.get('labelIds', []),
                'size_estimate': message.get('sizeEstimate', 0),
                'content': content,
                'attachments_count': len(content.attachments),
                'has_attachments': len(content.attachments) > 0
            }
            
        except HttpError as error:
            print(f"Erreur lors de la récupération du message {message_id}: {error}")
            return {}
            
    async def _extract_email_content(self, payload: Dict) -> EmailContent:
        """
        Extraction intelligente du contenu email à partir de la structure MIME
        Inspiré de la fonction extractEmailContent du projet Gmail-MCP-Server
        """
        content = EmailContent()
        
        def process_part(part: Dict, path: str = ""):
            """Traite récursivement les parties MIME"""
            mime_type = part.get('mimeType', '')
            
            # Traitement du contenu textuel
            if 'body' in part and 'data' in part['body']:
                try:
                    decoded_data = base64.urlsafe_b64decode(
                        part['body']['data'].encode('utf-8')
                    ).decode('utf-8')
                    
                    if mime_type == 'text/plain':
                        content.plain_text += decoded_data
                    elif mime_type == 'text/html':
                        content.html_content += decoded_data
                        
                except Exception as e:
                    print(f"Erreur décodage contenu: {e}")
            
            # Traitement des pièces jointes
            if 'body' in part and 'attachmentId' in part['body']:
                filename = part.get('filename', f'attachment-{part["body"]["attachmentId"]}')
                attachment = EmailAttachment(
                    id=part['body']['attachmentId'],
                    filename=filename,
                    mime_type=mime_type,
                    size=part['body'].get('size', 0),
                    download_id=part['body']['attachmentId']
                )
                content.attachments.append(attachment)
            
            # Traitement récursif des sous-parties
            if 'parts' in part:
                for i, subpart in enumerate(part['parts']):
                    process_part(subpart, f"{path}/part{i}")
        
        # Traitement de la charge utile principale
        process_part(payload)
        
        return content
        
    async def download_attachment(self, 
                                message_id: str, 
                                attachment_id: str,
                                save_path: str = "./downloads",
                                custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Télécharge une pièce jointe d'email
        Inspiré de la fonction download_attachment du projet Gmail-MCP-Server
        """
        try:
            # Récupération des données de la pièce jointe
            attachment = self.gmail.users().messages().attachments().get(
                userId=self.user_id,
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            if 'data' not in attachment:
                raise Exception("Aucune donnée d'attachement reçue")
            
            # Décodage des données base64
            file_data = base64.urlsafe_b64decode(attachment['data'])
            
            # Détermination du nom de fichier
            if not custom_filename:
                # Récupération du nom original depuis le message
                message = self.gmail.users().messages().get(
                    userId=self.user_id,
                    id=message_id,
                    format='full'
                ).execute()
                
                custom_filename = self._find_attachment_filename(
                    message.get('payload', {}), 
                    attachment_id
                ) or f"attachment_{attachment_id}"
            
            # Création du dossier de destination
            os.makedirs(save_path, exist_ok=True)
            
            # Sauvegarde du fichier
            file_path = os.path.join(save_path, custom_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': custom_filename,
                'size': len(file_data),
                'message': f"Pièce jointe téléchargée: {custom_filename}"
            }
            
        except Exception as error:
            return {
                'success': False,
                'error': str(error),
                'message': f"Erreur lors du téléchargement: {error}"
            }
            
    def _find_attachment_filename(self, payload: Dict, attachment_id: str) -> Optional[str]:
        """Trouve le nom de fichier original d'une pièce jointe"""
        def search_parts(part: Dict) -> Optional[str]:
            if ('body' in part and 
                'attachmentId' in part['body'] and 
                part['body']['attachmentId'] == attachment_id):
                return part.get('filename')
            
            if 'parts' in part:
                for subpart in part['parts']:
                    result = search_parts(subpart)
                    if result:
                        return result
            return None
        
        return search_parts(payload)
        
    async def batch_modify_emails(self, 
                                operation: BatchOperation) -> BatchOperation:
        """
        Opération par lot sur les emails
        Inspiré de la fonction batch_modify_emails du projet Gmail-MCP-Server
        """
        # Traitement par lots
        total_messages = len(operation.message_ids)
        
        for i in range(0, total_messages, operation.batch_size):
            batch = operation.message_ids[i:i + operation.batch_size]
            
            try:
                # Traitement du lot actuel
                for message_id in batch:
                    try:
                        # Construction de la requête de modification
                        modify_request = {}
                        if operation.add_labels:
                            modify_request['addLabelIds'] = operation.add_labels
                        if operation.remove_labels:
                            modify_request['removeLabelIds'] = operation.remove_labels
                        
                        # Exécution de la modification
                        self.gmail.users().messages().modify(
                            userId=self.user_id,
                            id=message_id,
                            body=modify_request
                        ).execute()
                        
                        operation.success_count += 1
                        
                    except Exception as e:
                        operation.failure_count += 1
                        operation.errors.append(f"Message {message_id}: {str(e)}")
                        
            except Exception as e:
                operation.errors.append(f"Erreur lot {i//operation.batch_size + 1}: {str(e)}")
        
        return operation
        
    async def batch_delete_emails(self, 
                                message_ids: List[str], 
                                batch_size: int = 50) -> Dict[str, Any]:
        """Suppression par lot d'emails"""
        operation = BatchOperation(
            message_ids=message_ids,
            operation_type="delete",
            batch_size=batch_size
        )
        
        total_messages = len(message_ids)
        
        for i in range(0, total_messages, batch_size):
            batch = message_ids[i:i + batch_size]
            
            try:
                for message_id in batch:
                    try:
                        self.gmail.users().messages().delete(
                            userId=self.user_id,
                            id=message_id
                        ).execute()
                        operation.success_count += 1
                    except Exception as e:
                        operation.failure_count += 1
                        operation.errors.append(f"Message {message_id}: {str(e)}")
                        
            except Exception as e:
                operation.errors.append(f"Erreur lot {i//batch_size + 1}: {str(e)}")
        
        return {
            'total_processed': total_messages,
            'success_count': operation.success_count,
            'failure_count': operation.failure_count,
            'errors': operation.errors
        }
        
    async def advanced_label_management(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Gestion avancée des labels Gmail
        Actions: create, update, delete, list, get_or_create
        """
        try:
            if action == "create":
                return await self._create_label(kwargs)
            elif action == "update":
                return await self._update_label(kwargs)
            elif action == "delete":
                return await self._delete_label(kwargs)
            elif action == "list":
                return await self._list_labels()
            elif action == "get_or_create":
                return await self._get_or_create_label(kwargs)
            else:
                return {'error': f'Action non supportée: {action}'}
                
        except Exception as error:
            return {'error': str(error)}
            
    async def _create_label(self, params: Dict) -> Dict[str, Any]:
        """Crée un nouveau label Gmail"""
        label_object = {
            'name': params['name'],
            'messageListVisibility': params.get('messageListVisibility', 'show'),
            'labelListVisibility': params.get('labelListVisibility', 'labelShow')
        }
        
        result = self.gmail.users().labels().create(
            userId=self.user_id,
            body=label_object
        ).execute()
        
        return {
            'success': True,
            'label': result,
            'message': f"Label '{params['name']}' créé avec succès"
        }
        
    async def _list_labels(self) -> Dict[str, Any]:
        """Liste tous les labels Gmail"""
        response = self.gmail.users().labels().list(userId=self.user_id).execute()
        labels = response.get('labels', [])
        
        # Classification des labels
        system_labels = [l for l in labels if l.get('type') == 'system']
        user_labels = [l for l in labels if l.get('type') == 'user']
        
        return {
            'all_labels': labels,
            'system_labels': system_labels,
            'user_labels': user_labels,
            'counts': {
                'total': len(labels),
                'system': len(system_labels),
                'user': len(user_labels)
            }
        }
        
    def build_advanced_search_query(self, criteria: Dict[str, Any]) -> str:
        """
        Construit une requête de recherche Gmail avancée
        
        Args:
            criteria: Dictionnaire des critères de recherche
        
        Returns:
            Chaîne de requête Gmail formatée
        """
        query_parts = []
        
        # Correspondance des critères avec les opérateurs Gmail
        operator_mapping = {
            'from': GmailSearchOperator.FROM.value,
            'to': GmailSearchOperator.TO.value,
            'subject': GmailSearchOperator.SUBJECT.value,
            'has_attachment': GmailSearchOperator.HAS_ATTACHMENT.value,
            'after': GmailSearchOperator.AFTER.value,
            'before': GmailSearchOperator.BEFORE.value,
            'is_unread': GmailSearchOperator.IS_UNREAD.value,
            'is_read': GmailSearchOperator.IS_READ.value,
            'is_important': GmailSearchOperator.IS_IMPORTANT.value,
            'label': GmailSearchOperator.LABEL.value,
            'larger': GmailSearchOperator.LARGER.value,
            'smaller': GmailSearchOperator.SMALLER.value,
            'category': GmailSearchOperator.CATEGORY.value
        }
        
        for criterion, value in criteria.items():
            if criterion in operator_mapping:
                if isinstance(value, bool) and value:
                    query_parts.append(operator_mapping[criterion].rstrip(':'))
                elif not isinstance(value, bool):
                    if criterion in ['subject'] and ' ' in str(value):
                        query_parts.append(f'{operator_mapping[criterion]}"{value}"')
                    else:
                        query_parts.append(f'{operator_mapping[criterion]}{value}')
        
        return ' '.join(query_parts)
        
    async def analyze_email_patterns(self, 
                                   timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Analyse les patterns d'emails sur une période
        Fonctionnalité inspirée du projet Gmail-MCP-Server pour l'IA
        """
        # Construction de la requête temporelle
        after_date = (datetime.now() - timedelta(days=timeframe_days)).strftime('%Y/%m/%d')
        query = f"after:{after_date}"
        
        # Recherche des emails de la période
        emails = await self.search_emails_advanced(query, max_results=500)
        
        # Analyse des patterns
        patterns = {
            'total_emails': len(emails),
            'senders_frequency': {},
            'attachment_emails': 0,
            'unread_emails': 0,
            'important_emails': 0,
            'average_size': 0,
            'mime_types': {},
            'time_distribution': {},
            'subject_keywords': {}
        }
        
        total_size = 0
        
        for email in emails:
            # Analyse des expéditeurs
            sender = email.get('from', 'unknown')
            patterns['senders_frequency'][sender] = patterns['senders_frequency'].get(sender, 0) + 1
            
            # Analyse des pièces jointes
            if email.get('has_attachments'):
                patterns['attachment_emails'] += 1
            
            # Analyse des labels
            labels = email.get('labels', [])
            if 'UNREAD' in labels:
                patterns['unread_emails'] += 1
            if 'IMPORTANT' in labels:
                patterns['important_emails'] += 1
            
            # Analyse de la taille
            size = email.get('size_estimate', 0)
            total_size += size
            
            # Analyse des mots-clés du sujet
            subject = email.get('subject', '').lower()
            words = re.findall(r'\b\w+\b', subject)
            for word in words:
                if len(word) > 3:  # Mots significatifs
                    patterns['subject_keywords'][word] = patterns['subject_keywords'].get(word, 0) + 1
        
        # Calculs finaux
        if patterns['total_emails'] > 0:
            patterns['average_size'] = total_size // patterns['total_emails']
        
        # Top senders et mots-clés
        patterns['top_senders'] = sorted(
            patterns['senders_frequency'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        patterns['top_keywords'] = sorted(
            patterns['subject_keywords'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]
        
        return patterns

class GmailMCPInspiredFeatures:
    """
    Fonctionnalités inspirées du projet Gmail-MCP-Server
    pour enrichir Sylvie v2.1
    """
    
    def __init__(self, gmail_service):
        self.gmail_manager = AdvancedGmailManager(gmail_service)
        
    async def smart_email_search(self, natural_query: str) -> List[Dict[str, Any]]:
        """
        Recherche intelligente basée sur le langage naturel
        Convertit les requêtes naturelles en syntaxe Gmail
        """
        # Conversion des phrases naturelles en opérateurs Gmail
        criteria = self._parse_natural_query(natural_query)
        
        # Construction de la requête Gmail
        gmail_query = self.gmail_manager.build_advanced_search_query(criteria)
        
        # Exécution de la recherche
        return await self.gmail_manager.search_emails_advanced(gmail_query)
        
    def _parse_natural_query(self, query: str) -> Dict[str, Any]:
        """Parse une requête en langage naturel vers des critères Gmail"""
        criteria = {}
        query_lower = query.lower()
        
        # Détection d'expéditeur
        from_patterns = [r'de (\S+@\S+)', r'from (\S+@\S+)', r'expéditeur (\S+@\S+)']
        for pattern in from_patterns:
            match = re.search(pattern, query_lower)
            if match:
                criteria['from'] = match.group(1)
        
        # Détection de sujet
        subject_patterns = [r'sujet[:\s]+([^,]+)', r'subject[:\s]+([^,]+)', r'objet[:\s]+([^,]+)']
        for pattern in subject_patterns:
            match = re.search(pattern, query_lower)
            if match:
                criteria['subject'] = match.group(1).strip()
        
        # Détection de pièces jointes
        if any(word in query_lower for word in ['pièce jointe', 'attachment', 'fichier', 'document']):
            criteria['has_attachment'] = True
        
        # Détection de statut
        if any(word in query_lower for word in ['non lu', 'unread', 'pas lu']):
            criteria['is_unread'] = True
        if any(word in query_lower for word in ['important', 'priorité', 'urgent']):
            criteria['is_important'] = True
        
        # Détection temporelle
        time_patterns = [
            (r'dernière semaine|last week', 7),
            (r'dernier mois|last month', 30),
            (r'cette semaine|this week', 7),
            (r'aujourd\'hui|today', 1),
            (r'hier|yesterday', 2)
        ]
        
        for pattern, days in time_patterns:
            if re.search(pattern, query_lower):
                after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
                criteria['after'] = after_date
                break
        
        return criteria
        
    async def generate_email_insights(self) -> Dict[str, Any]:
        """Génère des insights intelligents sur les emails"""
        # Analyse des patterns récents
        patterns = await self.gmail_manager.analyze_email_patterns(30)
        
        # Génération d'insights
        insights = {
            'productivity_score': self._calculate_productivity_score(patterns),
            'email_health': self._assess_email_health(patterns),
            'recommendations': self._generate_recommendations(patterns),
            'time_analysis': patterns.get('time_distribution', {}),
            'sender_analysis': patterns.get('top_senders', []),
            'keyword_trends': patterns.get('top_keywords', [])
        }
        
        return insights
        
    def _calculate_productivity_score(self, patterns: Dict) -> int:
        """Calcule un score de productivité email"""
        total = patterns.get('total_emails', 0)
        unread = patterns.get('unread_emails', 0)
        
        if total == 0:
            return 100
        
        read_ratio = (total - unread) / total
        return min(100, int(read_ratio * 100))
        
    def _assess_email_health(self, patterns: Dict) -> str:
        """Évalue la santé de la boîte email"""
        total = patterns.get('total_emails', 0)
        unread = patterns.get('unread_emails', 0)
        
        if total == 0:
            return "Excellent"
        
        unread_ratio = unread / total
        
        if unread_ratio < 0.1:
            return "Excellent"
        elif unread_ratio < 0.3:
            return "Bon"
        elif unread_ratio < 0.5:
            return "Correct"
        else:
            return "Besoin d'attention"
            
    def _generate_recommendations(self, patterns: Dict) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        unread_ratio = patterns.get('unread_emails', 0) / max(1, patterns.get('total_emails', 1))
        
        if unread_ratio > 0.3:
            recommendations.append("📧 Trop d'emails non lus - considérez un tri par priorité")
        
        if patterns.get('attachment_emails', 0) > patterns.get('total_emails', 1) * 0.5:
            recommendations.append("📎 Beaucoup de pièces jointes - archivez les anciens documents")
        
        top_senders = patterns.get('top_senders', [])
        if len(top_senders) > 0 and top_senders[0][1] > 20:
            recommendations.append(f"📬 {top_senders[0][0]} envoie beaucoup d'emails - configurez des filtres")
        
        return recommendations

# Export pour intégration dans Sylvie
__all__ = [
    'AdvancedGmailManager',
    'GmailMCPInspiredFeatures', 
    'EmailAttachment',
    'EmailContent',
    'BatchOperation',
    'GmailSearchOperator'
]
