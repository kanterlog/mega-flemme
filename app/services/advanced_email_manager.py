"""
🧠 Advanced Email Management pour Sylvie v2.0
Inspiré par langgraph-email-automation & aomail-ai
Fonctionnalités IA avancées pour la gestion intelligente des emails
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class EmailPriority(Enum):
    """Niveaux de priorité des emails"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

class EmailCategory(Enum):
    """Catégories d'emails"""
    BUSINESS_INQUIRY = "business_inquiry"
    MEETING_REQUEST = "meeting_request"
    FOLLOW_UP = "follow_up"
    TECHNICAL_ISSUE = "technical_issue"
    PERSONAL = "personal"
    NEWSLETTER = "newsletter"
    SPAM_SUSPICIOUS = "spam_suspicious"
    URGENT = "urgent"
    ADMINISTRATIVE = "administrative"

class ActionType(Enum):
    """Types d'actions requises"""
    REPLY_REQUIRED = "reply_required"
    SCHEDULE_MEETING = "schedule_meeting" 
    SEND_DOCUMENT = "send_document"
    PHONE_CALL = "phone_call"
    ACKNOWLEDGE_ONLY = "acknowledge_only"
    FORWARD_TO_TEAM = "forward_to_team"
    URGENT_ACTION = "urgent_action"

@dataclass
class EmailAnalysis:
    """Résultat de l'analyse d'un email"""
    category: EmailCategory
    priority: EmailPriority
    actions_required: List[ActionType]
    key_entities: List[str]
    sentiment: str
    time_references: Dict[str, Any]
    summary: str
    suggested_response: Optional[str] = None
    context_keywords: List[str] = None

class AdvancedEmailManager:
    """Manager avancé pour l'analyse et la gestion intelligente des emails"""
    
    def __init__(self):
        self.priority_keywords = {
            EmailPriority.CRITICAL: ["urgent", "critique", "panne", "erreur", "problème grave", "immédiat"],
            EmailPriority.HIGH: ["important", "deadline", "échéance", "rapidement", "asap", "priorité"],
            EmailPriority.MEDIUM: ["bientôt", "dès que possible", "cette semaine", "prochain"],
            EmailPriority.LOW: ["newsletter", "info", "fyi", "rappel", "notification"]
        }
        
        self.category_keywords = {
            EmailCategory.BUSINESS_INQUIRY: ["devis", "proposition", "projet", "business", "collaboration"],
            EmailCategory.MEETING_REQUEST: ["réunion", "meeting", "rendez-vous", "appel", "call", "conference"],
            EmailCategory.TECHNICAL_ISSUE: ["bug", "erreur", "problème", "technical", "serveur", "panne"],
            EmailCategory.FOLLOW_UP: ["suivi", "follow-up", "concernant", "suite à", "update"],
            EmailCategory.URGENT: ["urgent", "immédiat", "critique", "emergency", "asap"],
            EmailCategory.NEWSLETTER: ["newsletter", "nouvelles", "actualités", "unsubscribe"],
            EmailCategory.SPAM_SUSPICIOUS: ["cliquez ici", "gratuit", "gagnez", "promotion", "expire"]
        }
        
        self.action_patterns = {
            ActionType.REPLY_REQUIRED: [
                r"pouvez-vous.*?", r"pourriez-vous.*?", r"merci de.*?", 
                r"j'aimerais.*?", r"question.*?"
            ],
            ActionType.SCHEDULE_MEETING: [
                r"planifier.*réunion", r"programmer.*meeting", r"organiser.*call",
                r"disponible.*?", r"rdv.*?"
            ],
            ActionType.SEND_DOCUMENT: [
                r"envoyer.*document", r"transmettre.*fichier", r"joindre.*?",
                r"send.*file", r"attach.*?"
            ],
            ActionType.PHONE_CALL: [
                r"appeler", r"téléphoner", r"call me", r"phone.*?"
            ]
        }
        
    def analyze_email(self, subject: str, body: str, sender: str = "") -> EmailAnalysis:
        """
        Analyse complète d'un email
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email  
            sender: Expéditeur de l'email
            
        Returns:
            EmailAnalysis: Analyse complète de l'email
        """
        full_content = f"{subject} {body}".lower()
        
        # Analyse de priorité
        priority = self._detect_priority(full_content)
        
        # Catégorisation
        category = self._categorize_email(full_content, subject)
        
        # Extraction des actions
        actions = self._extract_actions(full_content)
        
        # Entités clés
        entities = self._extract_entities(body)
        
        # Sentiment
        sentiment = self._analyze_sentiment(full_content)
        
        # Références temporelles
        time_refs = self._extract_time_references(body)
        
        # Résumé
        summary = self._generate_summary(subject, body)
        
        # Mots-clés contextuels
        keywords = self._extract_context_keywords(full_content)
        
        return EmailAnalysis(
            category=category,
            priority=priority,
            actions_required=actions,
            key_entities=entities,
            sentiment=sentiment,
            time_references=time_refs,
            summary=summary,
            context_keywords=keywords
        )
    
    def _detect_priority(self, content: str) -> EmailPriority:
        """Détecte la priorité de l'email"""
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in content for keyword in keywords):
                return priority
        return EmailPriority.MEDIUM
    
    def _categorize_email(self, content: str, subject: str) -> EmailCategory:
        """Catégorise l'email"""
        # Score pour chaque catégorie
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            # Bonus pour les mots-clés dans le sujet
            score += sum(2 for keyword in keywords if keyword in subject.lower())
            scores[category] = score
            
        # Retourne la catégorie avec le score le plus élevé
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category
                
        return EmailCategory.BUSINESS_INQUIRY  # Défaut
    
    def _extract_actions(self, content: str) -> List[ActionType]:
        """Extrait les actions requises"""
        actions = []
        
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    actions.append(action_type)
                    break
                    
        # Si aucune action spécifique, détermine par défaut
        if not actions:
            if any(word in content for word in ["?", "question", "demande"]):
                actions.append(ActionType.REPLY_REQUIRED)
            else:
                actions.append(ActionType.ACKNOWLEDGE_ONLY)
                
        return list(set(actions))  # Évite les doublons
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extrait les entités importantes (noms, dates, etc.)"""
        entities = []
        
        # Extraction de dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)',
            r'(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)',
            r'(?:demain|aujourd\'hui|hier)'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
            
        # Extraction d'heures
        time_patterns = [
            r'\d{1,2}[h:]\d{0,2}',
            r'\d{1,2}\s*(?:heures?|h)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
            
        # Extraction de montants
        money_patterns = [
            r'\d+\s*(?:€|euros?|dollars?|\$)',
            r'(?:€|euros?|\$)\s*\d+'
        ]
        
        for pattern in money_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
            
        return entities
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyse basique du sentiment"""
        positive_words = ["merci", "excellent", "parfait", "content", "satisfait", "bravo"]
        negative_words = ["problème", "erreur", "déçu", "insatisfait", "urgent", "panne"]
        
        positive_score = sum(1 for word in positive_words if word in content)
        negative_score = sum(1 for word in negative_words if word in content)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def _extract_time_references(self, text: str) -> Dict[str, Any]:
        """Extrait les références temporelles"""
        time_refs = {}
        
        # Détection de dates relatives
        relative_dates = {
            "aujourd'hui": 0,
            "demain": 1,
            "après-demain": 2,
            "hier": -1,
            "avant-hier": -2
        }
        
        for phrase, delta in relative_dates.items():
            if phrase in text.lower():
                target_date = datetime.now() + timedelta(days=delta)
                time_refs['date'] = target_date.strftime('%Y-%m-%d')
                
        # Détection d'heures
        time_pattern = r'(\d{1,2})[h:](\d{0,2})'
        time_matches = re.findall(time_pattern, text)
        
        if time_matches:
            hour, minute = time_matches[0]
            minute = minute if minute else "00"
            time_refs['time'] = f"{hour.zfill(2)}:{minute.zfill(2)}"
            
        return time_refs
    
    def _generate_summary(self, subject: str, body: str) -> str:
        """Génère un résumé de l'email"""
        # Résumé basique : prend les premiers mots du corps
        words = body.split()[:15]
        summary = " ".join(words)
        
        if len(words) >= 15:
            summary += "..."
            
        return f"[{subject}] {summary}"
    
    def _extract_context_keywords(self, content: str) -> List[str]:
        """Extrait les mots-clés contextuels"""
        # Mots-clés techniques/business importants
        important_keywords = [
            "projet", "deadline", "budget", "équipe", "client", "serveur",
            "développement", "réunion", "présentation", "rapport", "formation",
            "contrat", "proposition", "devis", "planning", "ressources"
        ]
        
        found_keywords = [kw for kw in important_keywords if kw in content]
        return found_keywords
    
    def generate_smart_reply(self, analysis: EmailAnalysis, context: str = "") -> str:
        """
        Génère une réponse intelligente basée sur l'analyse
        
        Args:
            analysis: Analyse de l'email
            context: Contexte additionnel
            
        Returns:
            str: Suggestion de réponse
        """
        templates = {
            EmailCategory.MEETING_REQUEST: [
                "Merci pour votre message. Je vérifie mes disponibilités et reviens vers vous rapidement.",
                "Parfait, je peux me libérer {time_ref}. Confirmez-vous cette heure ?",
                "Excellente idée ! Proposez-vous un créneau particulier ?"
            ],
            EmailCategory.BUSINESS_INQUIRY: [
                "Merci pour votre intérêt. Je vous prépare une proposition détaillée.",
                "C'est un projet intéressant ! Pouvons-nous en discuter par téléphone ?",
                "Parfait, je vous envoie les informations demandées dans la journée."
            ],
            EmailCategory.FOLLOW_UP: [
                "Merci pour votre suivi. Voici le point sur l'avancement :",
                "Effectivement, faisons le point. Voici où nous en sommes :",
                "Merci de votre relance, je reviens vers vous avec les informations."
            ],
            EmailCategory.TECHNICAL_ISSUE: [
                "Je prends note du problème et m'en occupe immédiatement.",
                "Merci pour le signalement. Pouvez-vous me donner plus de détails ?",
                "Je transmets à l'équipe technique qui va intervenir rapidement."
            ]
        }
        
        # Sélection du template approprié
        category_templates = templates.get(analysis.category, [
            "Merci pour votre message, je reviens vers vous rapidement.",
            "J'ai bien reçu votre email et m'en occupe.",
            "Merci pour ces informations, je vous recontacte."
        ])
        
        # Sélection basée sur la priorité
        if analysis.priority == EmailPriority.CRITICAL:
            return "Je prends note de l'urgence et m'en occupe immédiatement. Je vous tiens informé des actions entreprises."
        elif analysis.priority == EmailPriority.HIGH:
            return category_templates[0]
        else:
            return category_templates[-1] if len(category_templates) > 1 else category_templates[0]
    
    def process_email_batch(self, emails: List[Dict[str, str]]) -> List[EmailAnalysis]:
        """
        Traite un lot d'emails en batch
        
        Args:
            emails: Liste d'emails avec 'subject', 'body', 'sender'
            
        Returns:
            List[EmailAnalysis]: Analyses de tous les emails
        """
        analyses = []
        
        for email in emails:
            analysis = self.analyze_email(
                email.get('subject', ''),
                email.get('body', ''),
                email.get('sender', '')
            )
            analyses.append(analysis)
            
        return analyses
    
    def get_priority_emails(self, analyses: List[EmailAnalysis]) -> List[EmailAnalysis]:
        """Retourne les emails par ordre de priorité"""
        priority_order = [
            EmailPriority.CRITICAL,
            EmailPriority.HIGH,
            EmailPriority.MEDIUM,
            EmailPriority.LOW
        ]
        
        sorted_emails = []
        for priority in priority_order:
            emails_of_priority = [a for a in analyses if a.priority == priority]
            sorted_emails.extend(emails_of_priority)
            
        return sorted_emails
    
    def get_action_summary(self, analyses: List[EmailAnalysis]) -> Dict[str, int]:
        """Retourne un résumé des actions requises"""
        action_counts = {}
        
        for analysis in analyses:
            for action in analysis.actions_required:
                action_counts[action.value] = action_counts.get(action.value, 0) + 1
                
        return action_counts

# Classes utilitaires pour l'intégration avec Sylvie
class SylvieEmailIntegration:
    """Intégration du système email avancé avec Sylvie"""
    
    def __init__(self):
        self.email_manager = AdvancedEmailManager()
        
    def analyze_incoming_email(self, email_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyse un email entrant pour Sylvie
        
        Returns:
            Dict avec l'analyse formatée pour Sylvie
        """
        analysis = self.email_manager.analyze_email(
            email_data.get('subject', ''),
            email_data.get('body', ''),
            email_data.get('sender', '')
        )
        
        return {
            'priority': analysis.priority.value,
            'category': analysis.category.value,
            'actions': [action.value for action in analysis.actions_required],
            'summary': analysis.summary,
            'sentiment': analysis.sentiment,
            'time_references': analysis.time_references,
            'keywords': analysis.context_keywords,
            'suggested_reply': self.email_manager.generate_smart_reply(analysis)
        }
    
    def process_user_request(self, request: str) -> Dict[str, Any]:
        """
        Traite une demande utilisateur liée aux emails
        
        Args:
            request: Demande de l'utilisateur (ex: "montre-moi mes emails urgents")
            
        Returns:
            Dict avec la réponse appropriée
        """
        request_lower = request.lower()
        
        if "urgent" in request_lower:
            return {
                'action': 'show_urgent_emails',
                'message': 'Je récupère vos emails urgents...'
            }
        elif "résumé" in request_lower or "summary" in request_lower:
            return {
                'action': 'email_summary', 
                'message': 'Voici un résumé de vos emails récents...'
            }
        elif "répondre" in request_lower or "reply" in request_lower:
            return {
                'action': 'smart_reply',
                'message': 'Je génère une réponse appropriée...'
            }
        elif "planning" in request_lower or "meeting" in request_lower:
            return {
                'action': 'extract_meetings',
                'message': 'J\'analyse vos demandes de réunion...'
            }
        else:
            return {
                'action': 'general_email_help',
                'message': 'Comment puis-je vous aider avec vos emails ?'
            }
